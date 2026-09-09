# Darwin Desbocatti - Podcast RSS Automatizado

Este proyecto genera y actualiza automáticamente un feed RSS estándar de podcasts a partir del Google Sheet con las columnas de Darwin Desbocatti (*No Toquen Nada*, DelSol 99.5 FM).

Los audios ya están alojados públicamente en la CDN de DelSol (`https://cdn.dl.uy/solmp3/...mp3`), por lo que **no es necesario descargar ni almacenar archivos pesados**. Todo se ejecuta 100% gratis con GitHub Actions y GitHub Pages.

---

## 🚀 Puesta en marcha paso a paso

### 1. Personalizar `config.json`
Abre [config.json](file:///root/scripts/darwin-podcast-feed/config.json) y ajusta:
* `owner_email`: **(MUY IMPORTANTE)** Pon tu correo electrónico real. Spotify te enviará un código de verificación de 8 dígitos a este correo cuando registres el podcast.
* `podcast_image`: URL de una imagen cuadrada (mínimo 1400x1400 px, máx 3000x3000 px). Es obligatoria para Spotify.
* `podcast_title`: Nombre con el que quieres que aparezca el podcast en Spotify.

### 2. Subir a GitHub
1. Crea un nuevo repositorio en GitHub (puede ser público).
2. Sube todos los archivos de esta carpeta:
   ```bash
   git init
   git add .
   git commit -m "Inicializar podcast RSS"
   git branch -M main
   git remote add origin https://github.com/TU_USUARIO/TU_REPOSITORIO.git
   git push -u origin main
   ```

### 3. Habilitar permisos de escritura para GitHub Actions
Para que el bot pueda actualizar automáticamente el archivo `feed.xml`:
1. En tu repositorio de GitHub, ve a **Settings** > **Actions** > **General**.
2. En la sección **Workflow permissions**, selecciona **Read and write permissions**.
3. Haz clic en **Save**.

### 4. Activar GitHub Pages (donde se hospeda el RSS)
1. En tu repositorio, ve a **Settings** > **Pages**.
2. En **Build and deployment** > **Branch**, selecciona `main` y la carpeta `/ (root)`.
3. Haz clic en **Save**.
4. En 1 o 2 minutos tendrás tu URL pública del feed:
   `https://TU_USUARIO.github.io/TU_REPOSITORIO/feed.xml`

### 5. Registrar en Spotify for Creators
1. Entra a [creators.spotify.com](https://creators.spotify.com).
2. Haz clic en **Empezar** o **Añadir nuevo show**.
3. Selecciona **"Ya tengo un feed RSS"** (o *"I already have an RSS feed"*).
4. Pega tu URL de GitHub Pages (`https://TU_USUARIO.github.io/TU_REPOSITORIO/feed.xml`).
5. Spotify leerá el feed y enviará un código de verificación al correo que pusiste en `owner_email`.
6. Ingresa el código y confirma.

---

## ⏰ ¿Cómo se actualiza?
* El flujo de GitHub Actions (`.github/workflows/update_feed.yml`) se ejecuta de lunes a viernes dos veces al día (12:00 y 15:00 de Uruguay).
* Si hay columnas nuevas en el Google Sheet, las agrega a `feed.xml`, hace commit y lo sube.
* GitHub Pages se actualiza en segundos, y Spotify detecta los nuevos episodios automáticamente.
* También puedes ejecutarlo manualmente en cualquier momento desde la pestaña **Actions** en GitHub haciendo clic en **Run workflow**.
