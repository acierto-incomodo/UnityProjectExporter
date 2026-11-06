const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const https = require('https');
const archiver = require('archiver');
const archiverCreate = archiver.default || archiver;
const log = require('electron-log');
const { autoUpdater } = require('electron-updater');

log.initialize();
log.info('Aplicación iniciando...');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 750,
    height: 720,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      nodeIntegration: false,
      contextIsolation: true
    }
  });

  mainWindow.loadFile('index.html');
}

app.whenReady().then(() => {
  createWindow();

  // Configuración de actualizaciones automáticas
  autoUpdater.logger = log;
  autoUpdater.logger.transports.file.level = 'info';
  autoUpdater.autoDownload = false; // Permite notificar y gestionar el proceso en el renderer

  autoUpdater.on('checking-for-update', () => {
    mainWindow.webContents.send('update-status', { status: 'checking', message: 'Comprobando actualizaciones...' });
  });

  autoUpdater.on('update-available', (info) => {
    mainWindow.webContents.send('update-status', { status: 'available', message: `Nueva versión disponible (${info.version}). Descargando actualización diferencial...` });
    autoUpdater.downloadUpdate();
  });

  autoUpdater.on('update-not-available', () => {
    mainWindow.webContents.send('update-status', { status: 'not-available', message: 'La aplicación está actualizada.' });
  });

  autoUpdater.on('download-progress', (progressObj) => {
    let msg = `Descargando actualización: ${Math.round(progressObj.percent)}% (${(progressObj.transferred / 1024 / 1024).toFixed(2)} MB / ${(progressObj.total / 1024 / 1024).toFixed(2)} MB)`;
    mainWindow.webContents.send('update-status', { status: 'downloading', message: msg, percent: progressObj.percent });
  });

  autoUpdater.on('update-downloaded', () => {
    mainWindow.webContents.send('update-status', { status: 'downloaded', message: '¡Actualización descargada con éxito!' });
  });

  autoUpdater.on('error', (err) => {
    log.error('Error en el auto-updater:', err);
    mainWindow.webContents.send('update-status', { status: 'error', message: 'Error al buscar actualizaciones.' });
  });

  // Comprobar actualizaciones al iniciar (solo en empaquetado)
  if (app.isPackaged) {
    autoUpdater.checkForUpdates().catch(err => log.error(err));
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// Selector de carpeta de Unity
ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, { properties: ['openDirectory'] });
  if (result.canceled || result.filePaths.length === 0) return null;

  const projectPath = result.filePaths[0];
  const items = fs.readdirSync(projectPath);
  const requiredList = ['Assets', 'ProjectSettings', 'Packages'];

  const scannedItems = items.map((itemName) => {
    const fullPath = path.join(projectPath, itemName);
    const isDir = fs.statSync(fullPath).isDirectory();
    const isRequired = requiredList.includes(itemName);

    return {
      name: itemName,
      isDirectory: isDir,
      required: isRequired,
      defaultChecked: isRequired
    };
  });

  return { projectPath, items: scannedItems };
});

// Exportar a ZIP
ipcMain.handle('export-zip', async (event, { projectPath, selectedItems }) => {
  try {
    const downloadsPath = app.getPath('downloads');
    const folderName = path.basename(projectPath);
    const zipName = `${folderName}_Backup_${Date.now()}.zip`;
    const outputPath = path.join(downloadsPath, zipName);

    const output = fs.createWriteStream(outputPath);
    const archive = archiverCreate('zip', { zlib: { level: 9 } }); // <--- AQUÍ

    return new Promise((resolve, reject) => {
      output.on('close', async () => {
        await shell.openPath(downloadsPath);
        resolve({ success: true, outputPath });
      });
      archive.on('error', (err) => reject(err));
      archive.pipe(output);

      for (const item of selectedItems) {
        const itemPath = path.join(projectPath, item);
        if (fs.existsSync(itemPath)) {
          const stat = fs.statSync(itemPath);
          if (stat.isDirectory()) {
            archive.directory(itemPath, item);
          } else {
            archive.file(itemPath, { name: item });
          }
        }
      }
      archive.finalize();
    });
  } catch (error) {
    log.error('Error en export-zip:', error);
    throw error;
  }
});

// Reiniciar aplicación para aplicar actualización
ipcMain.handle('restart-app', () => {
  autoUpdater.quitAndInstall(false, true);
});

// Obtener lista de versiones anteriores desde GitHub Releases
ipcMain.handle('get-versions', async () => {
  return new Promise((resolve) => {
    const options = {
      hostname: 'api.github.com',
      path: '/repos/acierto-incomodo/UnityProjectExporter/releases',
      headers: { 'User-Agent': 'UnityProjectExporter-App' }
    };

    https.get(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const releases = JSON.parse(data);
          if (Array.isArray(releases)) {
            const versions = releases.map(r => ({
              version: r.tag_name.replace('v', ''),
              name: r.name || r.tag_name,
              url: r.html_url
            }));
            resolve(versions);
          } else {
            resolve([]);
          }
        } catch (e) {
          resolve([]);
        }
      });
    }).on('error', () => resolve([]));
  });
});

// Abrir enlace externo de versión anterior en el navegador
ipcMain.handle('open-external-url', async (event, url) => {
  await shell.openExternal(url);
});