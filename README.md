# OmnAIView DevDataServer

This repository is part of the **OmnAI Project**, which aims to enhance the explorability of heterogeneous time-series data streams.
The **DevDataServer** provides a minimalistic implementation of various data streams that can be used with **OmnAIView** or other data consumers.
If you want to stay updated about the OmnAI Project, sign up for the [newsletter](https://omnaiscope.auto-intern.de/newsletter/).

## Getting Started
This Repository includes multiple servers in different languages. Each implementing the same idea of an OmnAIView-DataServer:

### Python:
Find the description on how to setup the dataserver at [this README](example_python/README.md#quickstart)


## Initializing a Datastream
Independent of the implementation-technology, the server will behave the same.
Testing the server-application requires a two step process:
1) Query available devices
2) Open a websocket-connection and request a specific device

This implements the workflow that is used in all OmnAIView prozesses.
A discovery is prepended to a connection.

#### Request the devices

```sh
curl -X GET http://localhost:8080/v1/get_devices
```

Your answer will encompass a list of available devices:

```json
{
  "datastreams": [
    {"UUID": "1002345", "color": {"r": 0, "g": 0, "b": 255}},
    {"UUID": "299345", "color": {"r": 255, "g": 0, "b": 0}}
  ]
}
```

#### Connect to websocket 
Use a CLI Websocket-Client to connect to the DevDataServer. 
With wscat you may run:
```
wscat -c ws://localhost:8080/v1/subscribe_ws
```

##### Receive data from the websocket 
With this connection opened, you can send a message to the server.
E.g. type the following command into your shell and hit `Return` to send it:

```sh
1002345 299345 100 json
```

The first two strings are the `UUID`s of the devices. 
The third string is the *sampling rate* that the websocket should provide to you.
The fourth string is the format of the datastream. 

The answer should be printed into your CLI and look something like this: 
```json
{
  "timestamp": 1742455130.314,
  "datastreams": ["1002345", "299345"],
  "data": [
    [0.0, 1.0]
  ]
}
```

You can change the strings and try out which answers you get. 
Possible formats are `json` and `csv`. 

It is important to understand, that this doesn't require the actual samplingrate of the device to change. The server is allowed to downsample a fast device for you.  
If a device is not producing enough data to fulfill the sampling rate, it will hold the latests available sample, ensuring, that the order of values within each websocket stays the same.
Even though, this is the default behavior, a later switch may be added to the DataServer that will drop non existent samples. This addition will not break existing behavior.

## Purpose

The DevDataServer serves two main purposes:

- **Development Support**: It provides a developer-friendly test environment for OmnAIView development.
- **Reference Implementation**: It serves as an example implementation for developers looking to create their own data servers.

## Contribution

For contribution guidelines, please refer to [CONTRIBUTIONS.md](CONTRIBUTIONS.md).

