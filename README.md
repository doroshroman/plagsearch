## How to run?

1. Open new terminal window and type:
    ```
    $ ganache-cli
    ```
    Copy 1 of 10 private key from output below.

2. Back to first terminal window and type:
    ```
    $ export PRIVATE_KEY=*copied private key*
    ```
3. Activate your virtual environment and install external dependencies from **requirements.txt**
4. Deploy smart contracts
    ```
    $ python3 blockchain/deploy.py
    ```
5. Run flask application
    ```
    $ flask run
    ```
