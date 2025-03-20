# Hydroponics-systems
Hardware and software solution for automtisation 


# Raspbian telepítése
Raspberry pi 2w: Raspberry PI OS LITE (64-bit); no desktop

# RPI beállítása
Rendszer frisítése:
```console
sudo apt update
```
```console
sudo apt upgrade
```
# Github projekt beállítása
Git telepítése: 
```console
sudo apt-get install git
```
Könyvtár klónozása:
```console
sudo git clone https://github.com/DanielBrenn/Hydroponics-systems.git
```


#  Docker container telepítése
Ha előzetesen volt telepítve docker container, akkor a következő parancssorral lehet lecserélni a régi verziót:

```console
$ for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
```
Ezután mivel nincs desktop környezet ezért a következő módon lehet a docker conatinert telpíteni:

```console
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

```console
# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

```console
# Install docker container
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
# Containerek letöltése
Legkönnyebben a különböző konténerek https://hub.docker.com/ oldalon találhatóak meg összefoglalva


A konténerek kezeléséhez webalapú kezeléséhez:
```console
docker pull portainer/portainer-ce:linux-arm 
```

A vezérlésért felelős grafikus felületen progrmaozható node-red:
nodered:
```console
docker pull nodered/node-red
```

Mqtt borker 
mosquitto
```console
docker pull eclipse-mosquitto
```

Data platform
influxDB
```console
docker pull influxdb:latest
```
Data visualisation
grafana
```console
docker pull grafana/grafana
```
# Containerek futtatása
Fontos megjegyezni, hogy minden egyes container egymástól függetlenül futnak.
  Tulajdonságaik ezeknek a containereknek:
    - Minden container saját erőforrásokkal rendelkezik->ha egy container összeomlik nem befolyásolja a többi modult
    - Saját virtuális hálózatot alkot (egyedi IP cím)
    - A hálózatokat docker container egy virtuális switch-el köti össze->egy containerek között van lehetőség TCP/IP protocollal kommunikálni, de containeren kívülre sükséges a prot forwarding 

Első lépésként beállítjuk a "restart policies" azaz megadjuk, hogy hogyan induljonanak el docker containerek indításkor. Cél az, hogy esteleges hiba esetén, illetve indításkor automatikus elinduljon.

A konténereken belüli file rendszer eléréséhez
```console
sudo docker run -ti -v $(pwd):/mnt ubuntu bash
```

```console
sudo docker run -d -p 9000:9000 --name=portainer --restart=always -v /var/run/docker.sock:/var/run/docker.sock -v portainer_data:/data portainer/portainer-ce:linux-arm
```

```console
sudo docker run -t -d -p 3000:3000 --name frontend --restart unless-stopped grafana/grafana
```

```console
sudo docker run -t -d -p 1880:1880 --restart unless-stopped -v -v node_red_data:/data --name logic nodered/node-red
```
Forrás: https://nodered.org/docs/getting-started/docker


```console
sudo docker run -t -d -p 8086:8086 --name  database --restart unless-stopped influxdb:latest
```

```console
sudo docker run -t -d -p 1883:1883 --name mqttbroker --restart unless-stopped eclipse-mosquitto
```

Indítás után a következő címeken érhetőek el a konténerek:
•Portainer: https://raspberrypi.local:9443/
•Grafana: raspberrypi.local:3000/
•Node Red: raspberrypi.local:1880/
•InfluxDB: raspberrypi.local:8086/
•Mosquitto: raspberrypi.local:1883/



# Access point inicilalizálása
Ez a funkció a későbbiekben a kész termék meglévő hálózatba való integrálásnál fogja betölteni a szerepét. 
Működése: az operációs rendszer felállása után közvetlenül az RPI lefuttat egy python scriptet, ami egy interupton keresztül (trigger high->low átmenet) figyeli GPIO4-es pint. 

Elsőként létre kell hozni a scriptet ami lefut amikor elindul az operációs rendszer:
Projekt mappába navigálunk:

```console
cd /
cd/home/Hydroponics-systems
```

A létehozzuk a launcher filet ami meghívja majd a scriptet
```console
sudo nano launcher.sh
```
Tartalma:
cd/
cd home/rpi4/Hydroponics-systems
sudo python3 access-point-set.py
cd/

Hydrophonics mapában létrehozunk egy log nevezetű mappát

Magát a launcher.sh corntrab háttérben futó sprogrammal lesz időzítve
```console
sudo crontab -e
```
@reboot sh /home/rpi4/bbt/launcher.sh >/home/rpi4/logs/cronlog 2>&1

# Node-red beállítása
Eddigekben a Node-red apaverziója lett telepítve, ami még nem alkalmas a RPI I/O pinjeinek a kezelésére, illetve nem tartalmazza még a kommunikációhoz szüksége protokoll csomagokat.

Következő módon lehet elérni a NODE-Red konténer belsejét (közvetlenül nem lehet CMD-ből elérni):

```console
sudo docker exec logic ls
```