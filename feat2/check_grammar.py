import language_tool_python
tool = language_tool_python.LanguageTool('fr')

# Correct answer, no grammatical errors
# text = "Les troupes du colonel Stark étaient situées à l'extrémité nord, le long de la clôture."

# With grammatical errors
text = "Les troupe du colonel Stark était situé à l'extrémitée nord, le long de la clôture."

"""
Errors made:

"troupe" should be "troupes" (incorrect singular form used).
"était" should be "étaient" (incorrect singular form of the verb used).
"situé" should be "situées" (incorrect singular and masculine form of the adjective used).
"extrémitée" should be "extrémité" (added an unnecessary "e" at the end).
"""

matches = tool.check(text)

print(len(matches))

for match in matches:
    print(match)

tool.close() # Call `close()` to shut off the server when you're done.