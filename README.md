# Darwin Desbocatti - Podcast RSS Automatizado

Este proyecto genera y actualiza automáticamente un feed RSS estándar de podcasts a partir del Google Sheet con las columnas de Darwin Desbocatti (*No Toquen Nada*, DelSol 99.5 FM).

Los audios ya están alojados públicamente en la CDN de DelSol (`https://cdn.dl.uy/solmp3/...mp3`), por lo que **no es necesario descargar ni almacenar archivos pesados**. Todo se ejecuta 100% gratis con GitHub Actions y GitHub Pages.

---

## 🚀 Puesta en marcha

### 1. Personalizar `config.json`
Abre [config.json](file:///root/scripts/darwin-podcast-feed/config.json) y ajusta:
* `owner_email`: **(MUY IMPORTANTE)** Pon el correo electrónico de tu cuenta de Spotify. Spotify te enviará un código de verificación de 8 dígitos a este correo cuando confirmes la redirección.
* `podcast_image`: URL de tu imagen de portada (mínimo 1400x1400 px).
* `podcast_title`: Nombre con el que quieres que aparezca el podcast en Spotify.

### 2. Subir a GitHub
El repositorio ya está inicializado y vinculado a `git@github.com:seniorcorel/darwin-podcast.git`.
Solo corre:
```bash
cd /root/scripts/darwin-podcast-feed
git push -u origin main
```

### 3. Habilitar permisos de escritura para GitHub Actions
Para que el bot de GitHub Actions pueda actualizar automáticamente el archivo `feed.xml`:
1. En tu repositorio [seniorcorel/darwin-podcast](https://github.com/seniorcorel/darwin-podcast), ve a **Settings** > **Actions** > **General**.
2. En la sección **Workflow permissions**, selecciona **Read and write permissions**.
3. Haz clic en **Save**.

### 4. Activar GitHub Pages (donde se hospeda el RSS)
1. En tu repositorio, ve a **Settings** > **Pages**.
2. En **Build and deployment** > **Branch**, selecciona `main` y la carpeta `/ (root)`.
3. Haz clic en **Save**.
4. En 1 o 2 minutos tu feed estará disponible públicamente en:
   **`https://seniorcorel.github.io/darwin-podcast/feed.xml`**

### 5. Redirigir tu podcast en Spotify for Creators
1. Entra en tu panel de [creators.spotify.com](https://creators.spotify.com).
2. Ve a los **Settings (Configuración)** de tu podcast existente.
3. Busca la sección **"Redirect your podcast" (Redirigir tu podcast)**.
4. Pega la URL de tu feed:
   `https://seniorcorel.github.io/darwin-podcast/feed.xml`
5. Spotify enviará un código de verificación a tu correo (`owner_email`). Ingrésalo y confirma.

¡Y listo! Tu podcast existente en Spotify comenzará a actualizarse automáticamente todos los días de lunes a viernes.
