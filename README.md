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
# NPM installálása 
Ez későbbiekben különbőző kiegészítők telepítéséshez
``` console
sudo apt-get install nodejs npm
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

A vezérlésért felelős grafikus felületen progrmaozható node-red (későbbiekben lesz telepítve docker konténeren kívül oka: lásd később):
~~nodered:~~

~~ocker pull nodered/node-red~~


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

~~IO kezeléséhez kell majd ~~
~~sudo docker run -d -p 8888:8888 --privileged --name gpiod corbosman/pigpiod ~~


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
sudo docker run -t -d -p 1880:1880 --restart unless-stopped -v /home/nodereddata:/data --name logic nodered/node-red
```
Részek funkciója:
--restart: esetleges leállást, hogyan kezelje a docker
-v: a conténer mapparendszerét  myNodeREDdata a konténeren kívülli rendszer mapparendszerrel /data (conténer:külső mappa)
--device: elérhetővé tesz a konténer számára konténeren kívüli erőforrások/mappák elérést
Forrás: 
https://nodered.org/docs/getting-started/docker
https://docs.docker.com/reference/cli/docker/container/run/#device

```console
sudo docker run -t -d -p 8086:8086 --name  database --restart unless-stopped influxdb:latest
```

~~sudo docker run -t -d -p 1883:1883 --name mqttbroker --restart unless-stopped eclipse-mosquitto~~


Indítás után a következő címeken érhetőek el a konténerek:
•Portainer: https://raspberrypi.local:9443/
•Grafana: raspberrypi.local:3000/
~~•Node Red: raspberrypi.local:1880/~~
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

access-point-set file tartalma:

```code
import RPi.GPIO as GPIO
import os
import time

BUTTON_GPIO = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
print("Script has started")

GPIO.wait_for_edge(BUTTON_GPIO, GPIO.FALLING)
print("Button was pushed")
os.system("sudo nmcli device disconnect wlan0")
os.system("sudo nmcli device up wlan0")
os.system("sudo nmcli device wifi hotspot ssid rpi4 password 12345678")
GPIO.cleanup()
```

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
DataType - Az eszköz adattípusát (3 féle): Jelenlegi érték (Current), Beállított érték (SetVal)(ha van), Kalibrációs és Jelleggörbe paraméterek (FunParam) (ha van)

{% rowheaders %}


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

{% endrowheaders %}
# Node-red

## Node-red telepítése docker konténeren kívül
Oka: mivel a konténeren belüli elemek nem képesek elérni közvetlenül a kernell szintű elemeket így a Node-red nem képes kiegészítő lépések nélkül vezérelni a GPIO portokat. Az előbb emített kiegészítő lépések minden egyes egyedi funkció/könyvtár telepítésénél szükséges elvégezni, emiatt új könyvtárak telepítése megnehezül, illetve minden könyvtár esetében egyedileg kell megoldani, hogy a kernell megfelelő részét elérje az adott modul/könyvtár.

## Node-red telepítése
Először navigáljuk a projekt könyvtárba
```console
  cd /home/rpi4/Hydroponics-systems/
```
Következő lépésben telepítjük a Node-Red modult:
```console
  bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
```
Majd beállítjuk, hogy a rendszer indításakor elinduljon a Node-red modul 

```console
sudo systemctl enable nodered.service
```
Fontos !! Node-red innetől kezdve a lokális hálózaton elérhető bárki által!!

## Node red specifikus infó:
•Node-Red indítása
  ```console
  node-red-start
  ```
•Node-Red beállítása:
  ```console
  node-red admin init
  ```
•Node-red eléréshi címe+port szám
  localhost:1880
•Important folders:
  Password management
  /etc/sudoers.d/010_pi-nopasswd
  Install-log:
  /var/log/nodered-install.log
  

## Node-red beállítása
Eddigekben a Node-red apaverziója lett telepítve, ami még nem alkalmas a RPI I/O pinjeinek a kezelésére, illetve nem tartalmazza még a kommunikációhoz szüksége protokoll csomagokat.

Modulok Node-Red:
•node-red
4.0.9
•node-red-contrib-ads1x15_i2c
0.0.14
•node-red-contrib-buffer-parser
3.2.2
•node-red-contrib-dht-sensor
1.0.4
•node-red-contrib-ds18b20-sensor
1.3.6
•node-red-contrib-influxdb
0.7.0
•node-red-contrib-play-audio
2.5.0
•node-red-node-pi-gpio
2.0.6
•node-red-node-ping
0.3.3
•node-red-node-pisrf
0.4.0
•node-red-node-random
0.4.1
•node-red-node-serialport
2.0.3
•node-red-node-smooth


DHT-11 szenzor:
```console
sudo npm install --unsafe-perm -g node-red-contrib-dht-sensor
 ```


<del>
  node-red-node-pi-gpiod
  /etc/rc.local filet /usr/bin/pigpiod sorral
  majd a noderedhez tartozó

  Ehhez szüksége kiegészíteni

  Következő módon lehet elérni a NODE-Red konténer belsejét (közvetlenül nem lehet CMD-ből elérni):
  ```console
  sudo docker exec -it logic bash 
  ```
  GPIO kezeléséhez telepíteni kell:
  ```console
  npm install node-red-contrib-gpio
  ```


  GPIO telepítése kernell szinten:
  Első lépésként navigéljunk a raspberry pi gyökérkönyvtárába:

  ```console
    sudo apt install git
    git clone https://github.com/WiringPi/WiringPi.git
    cd WiringPi
    ./build debian
    mv debian-template/wiringpi_3.14_arm64.deb . 
    sudo apt install ./wiringpi_3.14_arm64.deb 
  ```

  GPIO kezeléséhez:
    sudo apt-get install python3-rpi.gpio
</del>


# InfluxDB 
Az InfluxDB felelős az időben rögzített (time-series data) adatok rendszerezéséért és tárolásáért. 
Fontos megjegyezni InfluxDB v2 volt használva, mind a Node-Red, mind a Grafanaval való kapcsolatnál fontos lesz.
Az adatokat a következő logika szerint tárolja:

1. Bucket (TESTINGBUCKET): ez fogja össze az összes mért adatot fő gyűjtő kategória,

2. •Mesurment(Tesdata_n): alkategória amely a mérési adatcsomagokat választja szét jelen esetben különböző mérőkörökből (különálló rendszerből álló) adatokat foglalja össze
  •Field: mérési adattípusok szerint választja szét (pl. víz hőméréskletet(WTstate) és a levegő hőmérsékletet(ATstate) választja szét kategóriákra)
  •Tags: az adatokhoz kapcsolt metaadat ami az adatok további szűrésére szolgál (nem volt használva)
  •Timestamp: minden adatponthoz hozzá van rögzítve 
Ezek együttesen azonosítják az adatokat.


## InfluxDB beállítása
Beállításhoz el kell navigálni http://localhost:8086 címre vagy ha nem működik meg kell keresni a RPI IP címét hostname -i consol parancsal és a localhost helyére kell írni a parancs által adott ip címet. Ezután a következő lépéseket kell megtenni.

1. Be kell állítani az autentikációt
2. kreálni kell egy új Organizációt (Testing) (Később ehhez fogja küldeni az adatokat a Node-Red gyakorlatilag egy külön gyűjtő paraméter, amelyhez tartozik hozzáférési jogokkal rendelkezik)
3. Kreálni kell egy bucketet (TESTINGBUCKET) (Fő gyűjtő kategória)
4. Kreálni kell egy a buckethez tartozó api token-t/kulcsot írási és olvasási joggal (InfluxDB v2 sajátossága) 


## Kommunikáció Node-Red és InfluxDB között
A kommunikáció megvalósításához több feltételnek teljesülnie kell.
•Szükséges ismerni, hogy az InfluxDB milyen ip címe érhető el: http://localhost:8086 (Docker container beállításánál)
•Szükséges a kiválasztott bucketnek generált access token (InfluxDB ben kell beállítani)
•Ismerni kell az InluxDB Organization ID-t (EZ fogja azonosítani, hogy melyik "felhasználóhoz" fusson be az adat) (InfluxDB ben kell beállítani),
•Bucket nevére, melyik bucketbe lesz egységesen gyűjtve az adat, (InfluxDB ben kell beállítani).
•Measurment milyen measument néven lesz mentve az adott rendszerből származó adatot (Node-Red-től érkezik).


# Projekt felépítése és az eszközök kapcsolása

![Kapcs rajz](https://github.com/user-attachments/assets/d2893274-def7-48c9-8210-579c7a1ea96d)
