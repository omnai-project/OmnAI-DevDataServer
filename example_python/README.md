# Quickstart
1) Clone Repo
2) Build Environment
3) Launch Application
4) Request a Stream

```sh
git clone https://github.com/AI-Gruppe/OmnAIView-DevDataServer
cd OmnAIView-DevDataServer/example_python/
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python ./main.py
```

From another session you can now use a data-stream with a websocket-consumer of your choice. 
Read *Initializing a Datastream* to see how to work with the provided server.

## Python Example 

The example provides a dataserver for Version 2.0.0 of the Async API description. 
It implements a REST-API endpoint as well as a websocket endpoint on port 8080. 
Data from the datasource can be received in json and csv format. 
The first datastream is a sinus, the second a rectangular function. 
The timestamps are UNIX timestamps. 

### How to start the example 

To start the example make sure you have python3.12 (or newer) installed on your system. 

#### Create a test environment

Open your CLI. Use either Windows or Linux and navigate into the `example_python` sub-directory of this project.

Type the following command into your CLI: 

```sh
python3.12 -m venv env 
```

#### Start the environment

Depending on wether you are running Linux or Windows the command to activate a virtual environment looks a little different due to shell specifications.

On Linux:
```sh
source ./env/bin/activate
``` 

On Windows 
```sh
.\env\Scripts\activate 
```

If you want to learn more about managing Libraries with `venv` check out [this tutorial](https://github.com/STEMgraph/2d1d315d-bb92-48c0-b19f-19529a45e5ff).

#### Install Dependencies 

```sh
pip install -r requirements.txt
```

#### Run the script 
```sh
python ./main.py
```

If successfull you will receive the message: "Server running on port 8080 (HTTP & WebSocket)" in your Terminal.
Proceed with [initializing a datastream from your client](../README.md#initializing-a-datastream)





