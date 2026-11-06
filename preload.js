const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  selectFolder: () => ipcRenderer.invoke('select-folder'),
  exportZip: (data) => ipcRenderer.invoke('export-zip', data),
  restartApp: () => ipcRenderer.invoke('restart-app'),
  getVersions: () => ipcRenderer.invoke('get-versions'),
  openExternalUrl: (url) => ipcRenderer.invoke('open-external-url', url),
  onUpdateStatus: (callback) => ipcRenderer.on('update-status', (event, value) => callback(value))
});