const { app, BrowserWindow, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const fs = require('fs');
const archiver = require('archiver');
const log = require('electron-log');
const { autoUpdater } = require('electron-updater');

// Configuración de logs
log.initialize();
log.info('Aplicación iniciando...');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 750,
    height: 650,
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

  // Comprobar actualizaciones en producción
  autoUpdater.checkForUpdatesAndNotify().catch((err) => {
    log.error('Error al comprobar actualizaciones:', err);
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

// Selector de carpeta del proyecto Unity
ipcMain.handle('select-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });

  if (result.canceled || result.filePaths.length === 0) {
    return null;
  }

  const projectPath = result.filePaths[0];
  const items = fs.readdirSync(projectPath);

  // Elementos obligatorios para restaurar un proyecto Unity
  const requiredList = ['Assets', 'ProjectSettings', 'Packages'];

  const scannedItems = items.map((itemName) => {
    const fullPath = path.join(projectPath, itemName);
    const isDir = fs.statSync(fullPath).isDirectory();
    const isRequired = requiredList.includes(itemName);

    return {
      name: itemName,
      isDirectory: isDir,
      required: isRequired,
      // Los requeridos van marcados por defecto y no son opcionales
      defaultChecked: isRequired
    };
  });

  return {
    projectPath,
    items: scannedItems
  };
});

// Proceso de exportación a ZIP
ipcMain.handle('export-zip', async (event, { projectPath, selectedItems }) => {
  try {
    const downloadsPath = app.getPath('downloads');
    const folderName = path.basename(projectPath);
    const zipName = `${folderName}_Backup_${Date.now()}.zip`;
    const outputPath = path.join(downloadsPath, zipName);

    const output = fs.createWriteStream(outputPath);
    const archive = archiver('zip', { zlib: { level: 9 } });

    return new Promise((resolve, reject) => {
      output.on('close', async () => {
        log.info(`Archivo ZIP creado exitosamente (${archive.pointer()} bytes): ${outputPath}`);
        // Abrir la carpeta de descargas
        await shell.openPath(downloadsPath);
        resolve({ success: true, outputPath });
      });

      archive.on('error', (err) => {
        log.error('Error durante la compresión:', err);
        reject(err);
      });

      archive.pipe(output);

      // Añadir cada elemento seleccionado al ZIP
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