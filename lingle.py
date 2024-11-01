 # Imports the Google Cloud client library
from google.cloud import language_v1
from split_article import find_sentences

# Instantiates a client
client = language_v1.LanguageServiceClient()

# The text to analyze
with open("/Users/vector/Documents/GitHub/uofthacks6/article.txt", 'r', encoding="utf8") as text:
    text_to_read = text.read()

# Create a document for analysis
document = language_v1.Document(content=text_to_read, type_=language_v1.Document.Type.PLAIN_TEXT)

# Detects the sentiment of the text
sentiment = client.analyze_sentiment(document=document).document_sentiment

# Detects the entities and their sentiment within the text
response = client.analyze_entities(document=document, encoding_type=language_v1.EncodingType.UTF32)
response_two = client.analyze_entity_sentiment(document=document, encoding_type=language_v1.EncodingType.UTF32)

# Build lists for storing entity details
text_name = []
text_type = []
text_metadata = []
text_salience = []
text_score = []

# Ensure we only iterate up to the shorter of response entities
min_length = min(len(response.entities), len(response_two.entities))

for i in range(min_length):
    entity = response.entities[i]
    text_name.append(entity.name)
    text_type.append(entity.type_)
    text_metadata.append(entity.metadata)
    text_salience.append(entity.salience)
    text_score.append(response_two.entities[i].sentiment.score)

# Sort entities by salience in descending order
sorted_indices = sorted(range(len(text_salience)), key=lambda k: text_salience[k], reverse=True)
text_name = [text_name[i] for i in sorted_indices]
text_type = [text_type[i] for i in sorted_indices]
text_metadata = [text_metadata[i] for i in sorted_indices]
text_salience = [text_salience[i] for i in sorted_indices]
text_score = [text_score[i] for i in sorted_indices]

# Remove entities with type == OTHER
filtered_entities = [(name, score) for name, type_, score in zip(text_name, text_type, text_score)
                     if type_ != language_v1.Entity.Type.OTHER]
text_name, text_score = zip(*filtered_entities) if filtered_entities else ([], [])

# Get the top 3 entities based on salience
first_three_entities = text_name[:3]
first_three_entities_score = text_score[:3]

# Extract sentences containing the top entities
sentence_list = find_sentences(text_to_read)
yellow = []  # Sentences with neutral sentiment (0)
blue = []    # Sentences with negative sentiment (< 0)
red = []     # Sentences with positive sentiment (> 0)

for sentence in sentence_list:
    score = 0
    in_entity = False
    for entity, entity_score in zip(first_three_entities, first_three_entities_score):
        if entity in sentence:
            in_entity = True
            score += entity_score
            break  # Stop after finding the first relevant entity in the sentence

    if in_entity:
        if score == 0:
            yellow.append(sentence)
        elif score < 0:
            blue.append(sentence)
        else:
            red.append(sentence)

# Output categorized sentences
print("Neutral Sentences (Yellow):", yellow)
print("\nNegative Sentences (Blue):", blue)
print("\nPositive Sentences (Red):", red)

