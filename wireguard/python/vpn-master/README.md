# Installing

1. setup the python3 virtualenv

    ```bash
    sudo apt install -y python3-virtualenv
    ```

2. Install remaining dependencies

    ```bash
    python3 -m virtualenv --python="$(command -v python3)" .env &&
      source .env/bin/activate &&
      python3 -m pip install -U pip virtualenv &&
      python3 -m pip install -r requirements.txt

      ansible-galaxy install dev-sec.os-hardening
      ansible-galaxy install dev-sec.ssh-hardening
    ```
3. flash the Armbian Buster image onto your SD card

    Example using `dd`.  The path to your SD card (`/dev/sdd`) may be different, so be sure to update that to the correct device so that you dont accidentally wipe away one of your drives!

    ```bash
    sudo dd if=Armbian_19.11.4_Nanopineo2_buster_current_5.4.6.img of=/dev/sdd bs=1M
    ```

    Better yet, install (Etcher)[https://www.balena.io/etcher/] and use it to flash your SD card.  Its safer, and it will verify the write for you.

4. insert the SD card into your Nanopi Neo2 device and boot

5. ssh to your device(`ssh root@<IP of nanopi device here>`), change your root password, create a new user

    if you dont have a password manager that can generate good passwords for you, I suggest you use the following to generate a secure password.  Use as many characters as you can.  Do the same for the new user you create.  Dont worry, you wont need to use that password since you will be uploading an ssh key

    ```bash
    openssl rand 128 -base64
    ```

6. allow password-less sudo for your newly created user

    ```bash
    visudo
    ```

    change the line `%sudo   ALL=(ALL:ALL) ALL` to `%sudo   ALL=(ALL:ALL) NOPASSWD:ALL`

    Save the file and exit

7. logout of your device

8. Copy your ssh key to your device

    ```bash
    ssh-copy-id <username>@<IP of nanopi device here>
    ```

9. update `config.yml` to meet your requirements

10. run algo to deploy your VPN

    ```bash
    ./algo
    ```

    Follow the prompts, and wait for the procedure to complete

11. ssh to your new VPN (`ssh <username>@<IP of nanopi device here>`) and add some users

    ```bash
    sudo wgadmin add frank
    sudo wgadmin add lisa
    sudo wgadmin add tim
    sudo wgadmin sync
    sudo systemctl restart wg-quick@wg0

    # generate a QR code for your new user
    sudo cat /tmp/frank.conf | qrencode -t ansiutf8
    sudo rm /tmp/frank.conf
    ```

#  About

This repo is based on a stripped down version of [algo](https://github.com/trailofbits/algo)
