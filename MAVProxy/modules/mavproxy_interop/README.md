# interop

This is a MAVProxy interop module designed for use at the AUVSI competition.

For this module to work, you must clone the repo as "mavproxy_interop" into MAVProxy/modules

Also consider adding 'interop' to the default modules list so that the module will be loaded without needing to call module load interop


# Use

This module expects a json file to be stored in its directory with login info. It now tracks missions received from the interop server to give feedback on closest point of approach to each waypoint

login_data.json: A JSON object with the fields "server_url", "username" and "password"

See the example.

Type help in the MAVProxy console and look at all commands beginning with "interop" to see available commands.

Type "interop start" into the MAVProxy console to start interop. If you would like to use the now deprecated behavior of loading waypoints from a file, type "interop start file". Type "interop stop" to stop the server

# Contributions

Please do make an issue if you find a bug! It's very important that this script works exactly as intended, for obvious reasons. Feel free to also make an issue for a new feature request.

If you'd like to make changes, please do so on a different branch and make a pull request to merge your feature in so that others can review it ahead of time.

Email jms852@cornell.edu for any implementation or usage questions
