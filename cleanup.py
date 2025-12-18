import json

with open('all_jokes.json', 'r', encoding='utf-8') as f:
    jokes = json.load(f)

cleanuped_jokes = []

for joke in jokes:
    # combine part1 and part2
    # handle possible missing values
    part1 = joke.get('part1', '').strip()
    part2 = joke.get('part2', '').strip()
    full_joke = part1
    if part2:
        full_joke += ' ' + part2
    
    cleanuped_joke = {
        'joke': full_joke,
        'mature': joke.get('mature', False)
    }
    cleanuped_jokes.append(cleanuped_joke)

with open('jokes.json', 'w', encoding='utf-8') as file:
    json.dump(cleanuped_jokes, file, ensure_ascii=False, indent=4)

print(f"Cleaned up {len(jokes)} jokes and saved to jokes.json")
