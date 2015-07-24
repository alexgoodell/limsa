#!/usr/bin/ruby
#

while true do
  print "$ "
  $stdout.flush
  inputs = gets.strip
  puts "got your input: #{inputs}"
  # Check for termination, like if they type in 'exit' or whatever...
  # Run "system" on inputs like 'dir' or whatever...
end