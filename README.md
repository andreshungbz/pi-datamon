# pi-datamon

Data acquisition and monitoring system for temperature, humidity, and distance using a Raspberry Pi.

## Enabling I2C on Raspberry Pi

1. On Raspberry Pi OS, configure I2C then reboot.

```
sudo raspi-config
```

2. Optionally increase performance of I2C by adding the following to `/boot/config.txt`. Reboot afterwards.

```
dtparam=i2c_arm=on,i2c_baudrate=400000
```

3. Add your user to the `i2c` group then log out and back in. This is for accessing `i2c-tools`.

```
$ sudo usermod -a -G i2c $USER
```
