#!/usr/bin/ruby

filename = ARGV[0] + ".md"

File.open(filename) { |source_file|
	contents = source_file.read
	code_blocks = contents.scan(/```python\s(.*?)\s```/m )
	new_contents = code_blocks.join("\n")
	new_filename = ARGV[0] + ".py"
	File.open(new_filename, "w+") { |f| f.write(new_contents) }
}



