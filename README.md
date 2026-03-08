# rknpu-monitor
A simple web frontend to monitor the resources (including NPU) on Rockchip

Instructions:
1. Copy all the file on the same folder
```
git clone https://github.com/masterlog80/rknpu-monitor.git
cd rknpu-monitor
```
2. Build the docker image:
```
docker build -t rknpu-monitor .
```
3. Create the dockerfile (example):
```
services:
  rknpu-monitor:
    container_name: rknpu-monitor
    image: rknpu-monitor
    privileged: true
    networks:
      - proxy
    environment:
      - INTERVAL=1
    ports:
      - 8080:8080
    volumes:
      - [LOCAL FOLDER]:/data
      - /sys/kernel/debug:/sys/kernel/debug
    restart: unless-stopped

############

networks:
  proxy:
    external: true
```
4. Access with a web browser on URL: http://[LOCAL IP]:8080

Example:
<img width="1296" height="1023" alt="image" src="https://github.com/user-attachments/assets/c19bdfff-6154-44b3-8a86-e35dfe0cbb6c" />

Created with ChatGPT
