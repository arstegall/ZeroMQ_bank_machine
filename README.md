# ZeroMQ_bank_machine

There are three different scripts: client, broker and server.

**The client** app represents the phisical ATM itself. The client executes initial validations like PIN and credit card number combination.

**The brocker** transfers messages. It acts like proxy. It monitors traffic between server and client. All logs for monitoring system are saved in the brocker. The brocker also detects all errors and log them into the separate file. 

**The server** contains user data, checks PIN and credit card numbers. It also checks account balance and if the user is blocked.
