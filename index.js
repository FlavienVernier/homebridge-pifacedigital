var exec = require("child_process").exec;

const path = require('path');
const child_process = require('child_process');

var Service, Characteristic;

module.exports = function(homebridge) {
    Service = homebridge.hap.Service;
    Characteristic = homebridge.hap.Characteristic;
    //UUIDGen = homebridge.hap.uuid;
    
    homebridge.registerAccessory('homebridge-pifacedigital', 'PifaceDigital', PifaceDigitalAccessory);
}

function PifaceDigitalAccessory(log, config) {
    this.log = log;
    this.config = config || {"platform": "PifaceDigital"};

    this.name = config['name'];
    this.pin = config['pin'];
    this.io = config['io'];
    this.duration = config['duration'];

    if (this.io == "output"){
	this.log("add Switch " + this.name + " on pin " + this.pin );

	this.service = new Service.Switch(this.name, this.name);
	
	this.service
            .getCharacteristic(Characteristic.On)
            .on('get', this.getOn.bind(this))
            .on('set', this.setOn.bind(this));
    }else if (this.io == "input"){
	this.log("add Contact " + this.name + " on pin " + this.pin );

	this.service = new Service.ContactSensor(this.name, this.name);
	
	this.service
	    .getCharacteristic(Characteristic.ContactSensorState)
	    .setValue(false);
	
	
	//const cmpPath = path.join(__dirname, 'PifaceDigital.py');
	const cmpPath = path.join('/usr/local/bin/', 'PifaceDigital.py');
	const extCommand = ['-u', cmpPath, 'inputs', this.pin];
	
	this.log("Cmd input sensor: ", extCommand);
	this.helper = child_process.spawn('python3', extCommand);
	
	this.helper.stderr.on('data', (err) => {
	    throw new Error( `pifacedigital helper error: ${err})` );
	});

        this.helper.stdout.on('data', (data) => {
	    console.log(`data = |${data}|`);
	    const lines = data.toString().trim().split('\n');
	    for (let line of lines) {
		let [pin, state] = line.trim().split(' ');
		pin = parseInt(pin, 10);
		if (!isNaN(pin)){
		    state = !!parseInt(state, 10);
		    this.log("pin " + pin + " changed state to " + state);

		    this.service
			.getCharacteristic(Characteristic.ContactSensorState)
			.setValue(state);
		}
	    }
	});
    }
}

PifaceDigitalAccessory.prototype.getServices = function() {
    return [this.service];
}

PifaceDigitalAccessory.prototype.getOn = function(callback) {
    var self = this;
    var state_cmd = "PifaceDigital.py output " + this.pin + " status | grep 'output is on'";
    
    this.log(state_cmd);
    
    // Execute command to detect state
    exec(state_cmd, function (error, stdout, stderr) {
	var state = error ? false : true;

	// Error detection
	if (stderr) {
	    self.log("Failed to determine " + this.name + " state.");
	    self.log(stderr);
	}

	callback(stderr, state);
    });
    
    /*gpio.read(this.pin, function(err, value) {
	if (err) {
	    callback(err);
	} else {
	    var on = value;
	    callback(null, on);
	}
    });*/
}

PifaceDigitalAccessory.prototype.setOn = function(on, callback) {
    if (on) {
	this.pinAction(0);
	if (is_defined(this.duration) && is_int(this.duration)) {
	    this.pinTimer()
	}
	callback(null);
    } else {
	this.pinAction(1);
	callback(null);
    }
}

PifaceDigitalAccessory.prototype.pinAction = function(action) {
    this.log('Turning ' + (action == 0 ? 'on' : 'off') + ' pin #' + this.pin);

    var onoff_cmd = "PifaceDigital.py output " + this.pin + " " + (action == 0 ? 'on' : 'off');
    
    var self = this;
    // Execute command to set state
    exec(onoff_cmd, function (error, stdout, stderr){
	self.log("stdout: " + stdout);
	// Error detection
	if (error) {
	    self.log("Failed to turn " + (action == 0 ? "on " : "off ") + thisSwitch.name);
	    self.log(stderr);
	} else {
	    if (onoff_cmd)
		self.log(self.name + " is turned " + (action == 0 ? "on." : "off."));
	    //thisSwitch.state = state;
	    error = null;
	}
    });
    return true;
    /*gpio.open(self.pin, 'output', function() {
	gpio.write(self.pin, action, function() {
	    gpio.close(self.pin);
	    return true;
	});
    });*/
}

PifaceDigitalAccessory.prototype.pinTimer = function() {
    var self = this;
    setTimeout(function() {
	self.pinAction(1);
    }, this.duration);
}

var is_int = function(n) {
    return n % 1 === 0;
}

var is_defined = function(v) {
    return typeof v !== 'undefined';
}
