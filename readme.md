# Abraham_Userss — Gestió d'Usuaris

Script que llegeix el Google Sheet **Usuaris_Abraham** i crea o elimina usuaris del sistema automàticament. Un cop executat, buida el full de càlcul.

---

## Requisits

- Python 3
- Compte de Google Cloud amb la Google Sheets API habilitada
- Fitxer `credentials.json` inclòs al repositori

---

## Instal·lació

### 1. Instalar Python

#### Linux (Debian/Ubuntu/Trixie)
```bash
# Actualizar repositorios
sudo apt update

# Instalar Python3
sudo apt install python3 -y

# Verificar instalación
python3 --version

# Instalar pip (método 1 - directo)
sudo apt install python3-pip -y

# Si falla el método 1, usar método 2
sudo apt install wget -y
wget https://bootstrap.pypa.io/get-pip.py
sudo python3 get-pip.py --break-system-packages

# Verificar pip
pip3 --version
```

#### Windows
1. Descarga Python desde: https://www.python.org/downloads
2. Durante la instalación marca **"Add Python to PATH"**
3. Abre PowerShell y verifica:
```powershell
python --version
pip --version
```

---

### 2. Clonar el repositorio

#### Linux
```bash
# Instalar git y GitHub CLI
sudo apt install git gh -y

# Autenticarse en GitHub
gh auth login

# Clonar el repositorio
git clone https://github.com/icaparo-creator/Abraham_Userss.git
cd Abraham_Userss
```

#### Windows
1. Descarga Git: https://git-scm.com/download/win
2. Descarga GitHub CLI: https://cli.github.com
3. Abre PowerShell como Administrador y ejecuta:
```powershell
gh auth login
git clone https://github.com/icaparo-creator/Abraham_Userss.git
cd Abraham_Userss
```

---

### 3. Instalar dependencias

#### Opción A — Automática (con requirements.txt)

**Linux:**
```bash
pip3 install -r requeriments.txt --break-system-packages
```

**Windows (PowerShell como Administrador):**
```powershell
pip install -r requeriments.txt
```

#### Opción B — Manual (librería por librería)

**Linux:**
```bash
pip3 install google-api-python-client --break-system-packages
pip3 install google-auth --break-system-packages
```

**Windows (PowerShell como Administrador):**
```powershell
pip install google-api-python-client
pip install google-auth
```

---

## Uso

#### Linux (requiere root)
```bash
sudo python3 gestio_usuaris.py
```

#### Windows (PowerShell como Administrador)
```powershell
python gestio_usuaris.py
```

---

## Funcionamiento

1. Lee la columna **NOUS_USUARIS** del Google Sheet → crea los usuarios con contraseña `P@ssw0rd`
2. Lee la columna **USUARIS_ELIMINAR** → elimina los usuarios
3. Vacía el Google Sheet automáticamente

---

## Notas

- El script detecta automáticamente si se ejecuta en Windows o Linux
- Los usuarios se crean como usuarios estándar (sin permisos de administrador)
- El `credentials.json` está incluido en el repositorio privado
