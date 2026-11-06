# Borrar node_modules y el package-lock antiguo
rmdir /s /q node_modules
del package-lock.json

# Instalar permitiendo los scripts de post-instalación
npm install --foreground-scripts