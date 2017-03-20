'use strict';

const path = require('path');
const child_process = require('child_process');

let Service, Characteristic;

module.exports = (homebridge) => {
  Service = homebridge.hap.Service;
  Characteristic = homebridge.hap.Characteristic;

  homebridge.registerAccessory('homebridge-pifacedigital', 'PifaceDigital', PifaceDigitalPlugin);
};

class PifaceDigitalPlugin
{
  constructor(log, config) {
    this.log = log;
    this.name = config.name;
    // One possible setup:
    // ToDo
    this.pins = config.pins || {
      "Switch 0": 0,
      "Switch 1": 1,
      "Switch 2": 2,
      "Switch 3": 3
    };

    this.pin2contact = {};
    this.contacts = [];
    const helperPath = path.join(__dirname, 'pifacedigital.py');
    const args = ['-u', helperPath];

    for (let name of Object.keys(this.pins)) {
      const pin = this.pins[name];

      const subtype = name; 
      const contact = new Service.PifaceDigital(name, subtype);
      contact
        .getCharacteristic(Characteristic.PifaceDigitalState)
        .setValue(false);

      this.pin2contact[pin] = contact;
      this.contacts.push(contact);
      args.push(''+pin);
    }
    console.log('cmd contact sensors', this.pin2contact);
    this.helper = child_process.spawn('python', args);

    this.helper.stderr.on('data', (err) => {
      throw new Error(`pifacedigital helper error: ${err})`);
    }); 

    this.helper.stdout.on('data', (data) => {
      console.log(`data = |${data}|`);
      const lines = data.toString().trim().split('\n');
      for (let line of lines) {
        let [pin, state] = line.trim().split(' ');
        pin = parseInt(pin, 10);
        state = !!parseInt(state, 10);
        console.log(`pin ${pin} changed state to ${state}`);
  
        const contact = this.pin2contact[pin];
        if (!contact) throw new Error(`received pin event for unconfigured pin: ${pin}`);
        contact
          .getCharacteristic(Characteristic.PifaceDigitalState)
          .setValue(state);
      }
    });
  }

  getServices() {
    return this.contacts;
  }
}

