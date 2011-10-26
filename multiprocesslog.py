#!/usr/bin/env python
import os
import errno
import signal
import subprocess
import time
import yaml

try:
	f = open('multiprocesslog.yml', 'r')
	config = yaml.load(f)
finally:
	f.close()

def start_keepalive_command(entry):
	log = open(entry['log'], 'a')
	try:
		process = subprocess.Popen(entry['command'],
			stdout = log,
			stderr = log,
			shell = True)
		print "Started '" + entry['command'] + "' on PID", process.pid
	finally:
		log.close()
	return [process.pid]

def watch_non_keepalive_commands(entries):
	commands = []
	for entry in entries:
		entry['log_object'] = open(entry['log'], 'a')
		commands += entry['commands']
	print 'Watching the following commands:'
	for command in commands:
		print '  ', command
	print
	print 'Press Ctrl-C to stop.'
	
	try:
		while True:
			for entry in entries:
				log = entry['log_object']
				log.write("\n----------------------------\n")
				log.write(time.ctime() + "\n\n")
				for command in entry['commands']:
					log.write('# ' + command + "\n")
					log.flush()
					process = subprocess.Popen(command,
						stdout = log,
						stderr = log,
						shell = True)
					process.wait()
				log.write("\n")
				log.flush()
			time.sleep(4)
	finally:
		for entry in entries:
			entry['log_object'].close()

def kill_pids(pids):
	for pid in pids:
		print 'Killing PID', pid
		try:
			os.kill(pid, signal.SIGTERM)
		except OSError, e:
			if e.errno != errno.ECHILD and e.errno != errno.ESRCH:
				raise e
	for pid in pids:
		try:
			os.waitpid(pid, 0)
		except OSError, e:
			if e.errno != errno.ECHILD and e.errno != errno.ESRCH:
				raise e

def main():
	global config
	pids = []
	non_keepalive_commands = []
	
	try:
		for entry in config:
			if entry.get('keepalive'):
				pids += start_keepalive_command(entry)
			else:
				non_keepalive_commands.append(entry)
		watch_non_keepalive_commands(non_keepalive_commands)
	except KeyboardInterrupt:
		print 'Stopping...'
	finally:
		kill_pids(pids)

main()
