![](./imgs/venom.png)

# venom-auto

Venom Network auto using selenium framework
The script will automation almost task on [venom network tasks](https://venom.network/tasks):
- [x] [Stake Venom](https://venom.network/tasks/venom-stake)
- [x] [Venom Wallet](https://venom.network/tasks/venom-wallet)
- [x] [Web3 World](https://venom.network/tasks/web3-world)
- [x] [Venom Pad](https://venom.network/tasks/venom-pad)
- [x] [NFT Oasis_Gallery](https://venom.network/tasks/oasis-gallery)
- [ ] [Venom Bridge](https://venom.network/tasks/venom-bridge)
- [ ] [Venom Pools](https://venom.network/tasks/venom-pools)

## Install package
```sh
pip3 install -r requirements.txt
```
or using pipenv
```sh
pipenv sync
```

## Create wallet

```bash
cp .env-example .env
cp account.example.csv account.venom.csv
python3 wallet/venom/__init__.py
```

## Run app auto
    
```bash
python3 app/venom_stake.py
```


## Contact

[![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/bxdoan)
[![Twitter](https://img.shields.io/badge/Twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://twitter.com/bxdoan)
[![Email](https://img.shields.io/badge/Gmail-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:hi@bxdoan.com)

## Thanks for use
Buy me a coffee

[![buymecoffee](https://img.shields.io/badge/Buy_Me_A_Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://www.buymeacoffee.com/bxdoan)
[![bxdoan.eth](https://img.shields.io/badge/Ethereum-3C3C3D?style=for-the-badge&logo=Ethereum&logoColor=white)](https://etherscan.io/address/0x610322AeF748238C52E920a15Dd9A8845C9c0318)
[![paypal](	https://img.shields.io/badge/PayPal-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/bxdoan)
