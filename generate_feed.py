import csv
import json
import os
import sys
import re
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
import email.utils
import xml.etree.ElementTree as ET

# Timezone for Uruguay (UTC-3)
TZ_UY = timezone(timedelta(hours=-3))

def parse_date(date_str):
    """
    Parses dates from Google Sheet like '09/09/2026 1:20:32' or '23/09/2019 11:41:52'.
    Handles 12-hour AM/PM heuristic:
    - If hour is 1..7, it is treated as PM (13..19) because columns broadcast/upload in afternoon.
    - If hour is 8..12, it is treated as AM (8..12).
    """
    date_str = date_str.strip()
    if not date_str:
        return datetime.now(TZ_UY)
    
    parts = date_str.split(" ")
    if len(parts) == 2:
        date_part, time_part = parts
        try:
            d, m, y = map(int, date_part.split("/"))
            time_tokens = list(map(int, time_part.split(":")))
            h = time_tokens[0]
            minute = time_tokens[1] if len(time_tokens) > 1 else 0
            second = time_tokens[2] if len(time_tokens) > 2 else 0
            
            # 12-hour heuristic
            if h < 8:
                h += 12
            
            return datetime(y, m, d, h, minute, second, tzinfo=TZ_UY)
        except Exception:
            pass

    # Fallbacks
    for fmt in ("%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.replace(tzinfo=TZ_UY)
        except ValueError:
            pass
            
    return datetime.now(TZ_UY)

def get_audio_length(url, cache):
    if url in cache:
        return cache[url]
    try:
        req = urllib.request.Request(url, method="HEAD")
        req.add_header("User-Agent", "Mozilla/5.0 (Podcast Feed Generator)")
        with urllib.request.urlopen(req, timeout=3) as resp:
            cl = resp.headers.get("Content-Length")
            if cl and cl.isdigit():
                cache[url] = int(cl)
                return int(cl)
    except Exception:
        pass
    return 0

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, "config.json")
    cache_path = os.path.join(script_dir, "lengths_cache.json")
    output_path = os.path.join(script_dir, "feed.xml")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    print(f"Fetching sheet CSV from: {config['sheet_csv_url']}")
    req = urllib.request.Request(config["sheet_csv_url"])
    req.add_header("User-Agent", "Mozilla/5.0 (Podcast Feed Generator)")
    with urllib.request.urlopen(req, timeout=30) as resp:
        content = resp.read().decode("utf-8", errors="replace")

    reader = csv.DictReader(content.splitlines())
    valid_rows = []
    for row in reader:
        url = row.get("URL", "").strip()
        if url.startswith("http") and url.endswith(".mp3"):
            valid_rows.append(row)

    print(f"Total valid audio rows in sheet: {len(valid_rows)}")

    # Filter by date if configured
    rolling_days = config.get("rolling_days", 0)
    start_date_str = config.get("start_date", "").strip()

    if rolling_days > 0:
        cutoff_dt = datetime.now(TZ_UY) - timedelta(days=rolling_days)
        valid_rows = [r for r in valid_rows if parse_date(r.get("Fecha", "")) >= cutoff_dt]
        print(f"Filtered by rolling_days ({rolling_days} days): {len(valid_rows)} episodes.")
    elif start_date_str:
        start_dt = datetime.strptime(start_date_str, "%Y-%m-%d").replace(tzinfo=TZ_UY)
        valid_rows = [r for r in valid_rows if parse_date(r.get("Fecha", "")) >= start_dt]
        print(f"Filtered from start_date ({start_date_str}): {len(valid_rows)} episodes.")

    # Google Sheets is oldest first, podcast feeds are newest first
    valid_rows.reverse()

    max_episodes = config.get("max_episodes", 0)
    if max_episodes > 0:
        valid_rows = valid_rows[:max_episodes]
        print(f"Limiting to latest {max_episodes} episodes.")

    # Cache lengths for the newest episodes if not cached
    updated_cache = False
    for row in valid_rows[:15]:
        url = row["URL"].strip()
        if url not in cache:
            l = get_audio_length(url, cache)
            if l > 0:
                updated_cache = True

    if updated_cache:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)

    # Register XML namespaces
    ET.register_namespace("itunes", "http://www.itunes.com/dtds/podcast-1.0.dtd")
    ET.register_namespace("content", "http://purl.org/rss/1.0/modules/content/")

    rss = ET.Element("rss", {"version": "2.0"})
    channel = ET.SubElement(rss, "channel")

    title = ET.SubElement(channel, "title")
    title.text = config.get("podcast_title", "Darwin Desbocatti")

    link = ET.SubElement(channel, "link")
    link.text = config.get("podcast_link", "https://delsol.uy/notoquennada")

    desc = ET.SubElement(channel, "description")
    desc.text = config.get("podcast_description", "Columna de Darwin Desbocatti en No Toquen Nada.")

    lang = ET.SubElement(channel, "language")
    lang.text = config.get("podcast_language", "es-UY")

    generator = ET.SubElement(channel, "generator")
    generator.text = "Antigravity Darwin RSS Generator"

    author = ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}author")
    author.text = config.get("podcast_author", "Darwin Desbocatti")

    summary = ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}summary")
    summary.text = config.get("podcast_description", "Columna de Darwin Desbocatti en No Toquen Nada.")

    ptype = ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}type")
    ptype.text = "episodic"

    explicit = ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit")
    explicit.text = config.get("podcast_explicit", "no")

    owner = ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}owner")
    owner_name = ET.SubElement(owner, "{http://www.itunes.com/dtds/podcast-1.0.dtd}name")
    owner_name.text = config.get("owner_name", "Darwin Desbocatti")
    owner_email = ET.SubElement(owner, "{http://www.itunes.com/dtds/podcast-1.0.dtd}email")
    owner_email.text = config.get("owner_email", "seniorcorel@hotmail.com")

    image_url = config.get("podcast_image", "")
    if image_url:
        ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}image", {"href": image_url})
        image_el = ET.SubElement(channel, "image")
        img_url_el = ET.SubElement(image_el, "url")
        img_url_el.text = image_url
        img_title_el = ET.SubElement(image_el, "title")
        img_title_el.text = config.get("podcast_title", "Darwin Desbocatti")
        img_link_el = ET.SubElement(image_el, "link")
        img_link_el.text = config.get("podcast_link", "https://delsol.uy/notoquennada")

    category_text = config.get("podcast_category", "Comedy")
    ET.SubElement(channel, "{http://www.itunes.com/dtds/podcast-1.0.dtd}category", {"text": category_text})

    # Add items
    for row in valid_rows:
        raw_title = row.get("Titulo", "").strip() or "Columna de Darwin Desbocatti"
        title_no_date = re.sub(r"^\d{4}-\d{2}-\d{2}\s*-\s*", "", raw_title).strip()
        raw_desc = row.get("Descripcion", "").strip()

        if raw_desc and raw_desc != title_no_date:
            combined_desc = f"{title_no_date}\n\n{raw_desc}"
        else:
            combined_desc = title_no_date

        ep_url = row.get("URL", "").strip()
        ep_date_str = row.get("Fecha", "").strip()
        ep_dt = parse_date(ep_date_str)
        rfc_date = email.utils.format_datetime(ep_dt)

        length = cache.get(ep_url, 0)
        guid_str = ep_url

        date_prefix = ep_dt.strftime("%Y-%m-%d")
        full_title = f"{date_prefix} - {title_no_date}"

        item = ET.SubElement(channel, "item")
        
        ititle = ET.SubElement(item, "title")
        ititle.text = full_title

        itunes_title = ET.SubElement(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}title")
        itunes_title.text = full_title

        idesc = ET.SubElement(item, "description")
        idesc.text = combined_desc

        itunes_summary = ET.SubElement(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}summary")
        itunes_summary.text = combined_desc

        ilink = ET.SubElement(item, "link")
        ilink.text = ep_url

        iguid = ET.SubElement(item, "guid", {"isPermaLink": "false"})
        iguid.text = guid_str

        ipub = ET.SubElement(item, "pubDate")
        ipub.text = rfc_date

        ET.SubElement(item, "enclosure", {
            "url": ep_url,
            "length": str(length),
            "type": "audio/mpeg"
        })

        iexplicit = ET.SubElement(item, "{http://www.itunes.com/dtds/podcast-1.0.dtd}explicit")
        iexplicit.text = "no"

    ET.indent(rss, space="  ")
    
    xml_header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_data = ET.tostring(rss, encoding="utf-8").decode("utf-8")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(xml_header + xml_data)

    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"Generated {output_path} successfully ({file_size_kb:.1f} KB, {len(valid_rows)} episodes).")

if __name__ == "__main__":
    main()
