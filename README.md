# pge-csvparser
Python program to parse monthly PGE data for personal use. Outputs rates for absentee tenants, present tenants, and one rate for A/C overcharges.

## Usage
1. Download your usage details from PGE Dashboard > Energy Usage Details > Green Button download
   * Might be updated in the future to use PGE API's
2. Run python program with csv file(s) in same directory. Will export session to a new txt file.

## Notes: 
* Outputted data is customized for my personal use. Other relevant data can be manipulated fairly easily. Examples of outputs can be found in /Examples/. 
* Change commented line in overchargeParser() accordingly for general monthly usage.
* Remove overcharge calculation and update equations to calculate rates for AC/Heater usage fairly.
