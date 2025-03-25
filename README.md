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

# MQTT protokkol

## Mqtt általánosan:
Az MQTT egy publis-subscribe alapon működő kommunikációs protokol, ahol az eszközök/adatgyűjtők (edge devices) egy központi szerverhez kapcsolódnak (MQTT broker) amin keresztül különböző topikokra/témákra iratkoznak fel. Adott eszközök adott topikokra iratkoznak fel az MQTT brokeren keresztül, így az eszközök kommunikáció szempontjából el vannak egymástól választva a broker által. 
## Topicról általánosan:
A topic azonosítja a kommunikációt pontosabban az elérendő információt, a feriatkozott eszközök között teremt kapcsolatot valamilyen tetszőleges logika szerint. Más szavakkal a topic információt címez meg tetszőleges logikával és ez az infromációt csak az arra feliratkozott eszközök érhetik el- ez képzi a kommunikációs csatornát.
Egy topik egy eszköz számára lehet írható (publish), olvasható(subscribe) vagy egyszerre a kettő. Egy topic több eszköz által is elérhető lehet.
A topicoc hierarhicus vagy többszintetes információ azonosítást tesz lehetővé.

Szintek közötti alárendeltség:

level1/ level2a/  level3a1  ...
level1/ level2b   ..
level1/ level2c   ...
level1/ level2d   ...
level1/ level2d/  level3d1  ...
level1/ level2d/  level3d2  ...
level1/ level2d/  level3d3  ...
level1/ level2d/  level3d4  ...

Hidroponiás rendszer esetében a következő struktúra lesz alkalmazva:

{% rowheaders %}

|level1       | level2 | level3  | 
|-------------|--------|---------|
|DataCol      |DataType|DataValue|

{% endrowheaders %}

Ahol:
DataCol - Adatgyűjtőt azonosítja
DataType - Az eszköz adattípusát (3 féle): Jelenlegi érték, Beállított érték (ha van), Kalibrációs és Jelleggörbe paraméterek (ha van)

|DataType                       | 
|---------|---------|-----------|
|Current  | SetVal  | FunParam  | 
|---------|---------|-----------|
|ECstate 	|ECset 		|ECcp1V		  |
| 		    | 		    |ECcp2V		  |
| 		    | 		    |ECcp1CONC	|
| 		    | 		    |ECcp2CONC	|
|Phstate 	|Phset 		|PHcp1V		  |
| 		    | 		    |PHcp2V		  |
| 		    | 		    |PHcp1PH 	  |
| 		    | 		    |PHcp2PH	  |
|NO3state	|NO3set 	|NO3cp1V	  |
| 		    | 		    |NO3cp2V	  |
| 		    | 		    |NO3cp2CONC	|
| 		    | 		    |NO3cp1CONC	|
|Kstate 	|Kset 		|Kcp1V	 	  |
| 		    | 		    |Kcp2V		  |
| 		    | 		    |Kcp1CONC	  |
| 		    | 		    |Kcp2CONC	  |
|Castate 	|Caset 		|Cacp1V		  |
| 		    | 		    |Cacp2V		  |
| 		    | 		    |Cacp1CONC	|
| 		    | 		    |Cacp2CONC	|
|Mgstate 	|Mgset 		|Mgcp1V		  |
| 		    | 		    |Mgcp2V		  |
| 		    | 		    |Mgcp1CONC	|
| 		    | 		    |Mgcp2CONC	|
|Kstate 	|Kset 		|Kcp1V		  |
| 		    | 		    |Kcp2V		  |
| 		    | 		    |Kcp1CONC	  |
| 		    | 		    |Kcp2CONC	  |
|WTstate 	|WTset 		|Wvolume	  |
| 		    | 		    |Whp 		    |
|ATstate 	|ATset 		|RV 		    |
| 		    | 		    |HSP 		    |
|AHstate 	|AHset 		|RV 		    |
| 		    | 		    |HP 		    |
|WLstate 	|WLset 		|WContCross	|
| 		    | 		    |WlevSenOFFset	|
|PPI1state|- 		    |PPparam1	|
|PPI2state|- 		    |PPparam2	|
|PPI3state|- 		    |PPparam3	|
|PPI4state|- 		    |PPparam4	|
|PPI5state|- 		    |PPparam4	|
|RecPumpstate|RecWCurset|RecPumpParam	|
|MixPumpstate|MixWCurset|MixPumpParam	|


# Node-red beállítása
Eddigekben a Node-red apaverziója lett telepítve, ami még nem alkalmas a RPI I/O pinjeinek a kezelésére, illetve nem tartalmazza még a kommunikációhoz szüksége protokoll csomagokat.

Következő módon lehet elérni a NODE-Red konténer belsejét (közvetlenül nem lehet CMD-ből elérni):

```console
sudo docker exec logic ls
```


