import nltk
from nltk.tokenize import word_tokenize
import nltk.corpus
from nltk.corpus import stopwords
import warnings
import pandas as pd
import string
from string import printable
import random
import time
import spellchecker


spell = spellchecker.SpellChecker()
spell.word_frequency.load_words(['technion', 'haifa', 'ziv', 'neve', 'nave', 'shaanan'])
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('gutenberg')
warnings.filterwarnings(action='ignore')

GREETING_INPUTS = ("hello", "hi", "greetings", "sup", "what's up", "hey",)
WHATSAPP = ['hi how are you', 'how are you', "what's up", 'hi there', 'sup', 'how are you doing']
WHATSAPP_RESPONSES = ["I'm great! Thanks", 'Wonderful thanks!', 'Everything is great thanks!']
GREETING_RESPONSES = ["hi", "hey", "howdy", "hi there", "hello"]
THANKS_RESPONSES = ["You are welcome!", "Sure, no problem.", "Gladly", "Sure thing!", "Glad to assist."]
POSITIVE_INPUTS = ("yes", "sure", "ok", "yes please", "k", "cool", "great", 'ok cool', 'awesome', 'yup', 'yhh')
NEGATIVE_INPUTS = ("no", "no thanks", "na", "i'll pass", "forget it", "never mind",)
LIMIT_INPUTS = ("up to", "not more than", "maximum", "max")
STOPWORDS_ADD_ON = GREETING_RESPONSES + WHATSAPP + ["find", "i", "need", "to", "please", "want", "apartment",
                                                    "something", "next", "would", "like", "lower", 'less', 'cheaper']
ROOMS_WORD = ['bd', 'rooms', 'room', 'space', 'spaces', 'bed room', 'bed rooms', 'bedroom', 'bedrooms', 'nis', 'shekels']
ROOMMATES = ['roommate', 'roommates', 'room-mates', 'flatmates']
NO_ROOMMATES = ['without roommate', 'without roommates', 'without room-mates', 'no roommate', 'no roommates',
                'no room-mates', 'no flatmates', 'without flatmates']
NUMBERS_DICT = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven', 8: 'eight'}
NUMBERS_DICT_REVERS = {value: key for key, value in NUMBERS_DICT.items()}
FACTS = ["A year on Mercury is just 88 days long.",
         "Despite being farther from the Sun, Venus experiences higher temperatures than Mercury.",
         "On Mars, the Sun appears about half the size as it does on Earth.",
         "Jupiter has the shortest day of all the planets.",
         "The Sun is an almost perfect sphere."]
TELL_MY_FACT = ['tell me a fact', 'please tell me a fact', 'fact']

# Get data frame, drop empty values of post text and set post id as index
df = pd.read_csv("57812275694_posts.csv")
df = df[df['text'].notna()]
df = df[df['post_id'].notna()]
# df = df.set_index('post_id')

# Clean Data from Non-ASCII characters
st = set(printable)
for col in ('text', 'post_text', 'shared_text'):
    df[col] = df[col].astype(str)
    df[col] = df[col].apply(lambda x: ''.join(["" if i not in st else i for i in x]))


def main():
    start_chatbot()


def get_user_query(df, input):
    """
        This Function queries the saved database to find desired results.
        it will parse the user input into single word to be looked up in each post in the data.
        for searcing using nltk package it will initiate function get_all_phases_containing_tar_wrd.
        Parameters:
        df (pd.DataFrame): The saved database in Dataframe format.
        input (string): the user input.
        Returns:
        pd.DataFrame: results - a filtered dataframe with the queried results on no results.
    """
    df1 = df.copy()
    for item in input:
        df1[item] = 0
    posts = df1['post_text'].tolist()
    for i in range(len(posts)):
        x = posts[i].lower()
        x = x.replace('-', ' ').replace('!', ' ').replace('.', ' ').replace(',', '').replace('?', ' ')
        if x == 'nan' or x is None or x.lower == 'none':
            continue
        for item in input:
            item_index = input.index(item)
            if item.isdigit():
                if 'price' in input or int(item) > 500:
                    for price in range(0, int(item)+100, 50):
                        exist = get_all_phases_containing_tar_wrd(str(price), x)
                        if exist:
                            df1.iat[i, (12 + item_index)] = 1
                            break
            elif item in ROOMS_WORD:
                rooms_str = ''
                if item_index > 0:
                    rooms_str = input[item_index - 1]
                for room_word in ROOMS_WORD:
                    roo_search_str = rooms_str + ' ' + room_word
                    exist = get_all_phases_containing_tar_wrd(roo_search_str, x)
                    if not exist:
                        if rooms_str.isdigit():
                            if rooms_str in NUMBERS_DICT.keys():
                                roo_search_str = NUMBERS_DICT[int(rooms_str)] + ' ' + room_word
                                exist = get_all_phases_containing_tar_wrd(roo_search_str, x)
                        else:
                            if rooms_str in NUMBERS_DICT_REVERS.keys():
                                roo_search_str = str(NUMBERS_DICT_REVERS[rooms_str]) + ' ' + room_word
                                exist = get_all_phases_containing_tar_wrd(roo_search_str, x)
                    if exist:
                        df1.iat[i, (12 + item_index)] = 1
                        if input[item_index - 1] in NUMBERS_DICT_REVERS.keys() or int(input[item_index - 1]) in NUMBERS_DICT.keys():
                            df1.iat[i, (12 + item_index - 1)] = 1
                        else:
                            if input[item_index - 2] in NUMBERS_DICT_REVERS.keys() or input[
                                item_index - 2] in NUMBERS_DICT.keys():
                                df1.iat[i, (12 + item_index - 2)] = 1
                        break
            elif item in ROOMMATES:
                for roommate_word in ROOMMATES:
                    exist = get_all_phases_containing_tar_wrd(roommate_word, x)
                    if exist:
                        df1.iat[i, (12 + item_index)] = 1
            elif item in NO_ROOMMATES:
                count = 0
                for roommate_word in ROOMMATES:
                    exist = get_all_phases_containing_tar_wrd(roommate_word, x)
                    if exist:
                        count = 1
                    if count == 0:
                        df1.iat[i, (12 + item_index)] = 1
            else:
                if not item in NUMBERS_DICT and not item in NUMBERS_DICT_REVERS:
                    exist = get_all_phases_containing_tar_wrd(item, x)
                    if exist:
                        df1.iat[i, (12 + item_index)] = 1
                        break
    res_df = df1
    for item in input:
        res_df = res_df.loc[res_df[item] == 1]
    res_df = res_df.set_index('post_id')
    return res_df


def create_rooms_str(tokens, room_number, token):
    rooms_str = ''
    if not tokens[room_number].isdigit():
        if tokens[room_number] in NUMBERS_DICT_REVERS:
            rooms_str = tokens[room_number] + ' ' + token
    elif tokens[room_number].isdigit():
        rooms_str = tokens[room_number] + ' ' + token
    return rooms_str


def get_all_phases_containing_tar_wrd(target_word, tar_passage):
    """
        Since nltk Concordance function only prints the sentence it finds,
        this function's purpose is to enable saving concordance results

        str target_word, str tar_passage int left_margin int right_margin --> list of str
        left_margin and right_margin allocate the number of words/pununciation before and after target word
        Left margin will take note of the beginning of the text
    """
    # Create list of tokens using nltk function
    tokens = nltk.word_tokenize(tar_passage)
    for token in tokens:
        if token in ROOMS_WORD:
            room2_number = tokens.index(token) - 1
            rooms_str = create_rooms_str(tokens, room2_number, token)
            if rooms_str:
                tokens.remove(token)
                tokens.remove(tokens[room2_number])
                tokens.append(rooms_str)

    if target_word in tokens:
    # tokens = [word.lower() for word in words if word.isalpha()]
        return True

def response(user_response):
    """
        This Function collects the user input and processes it in order to generate a response
        after processing it will pass the user request to function get_user_query for database query.
        Parameters:
        user_response (string): Collect user Console input to be processed for chatbot reply.
        Returns:
        pd.DataFrame: results - a dataframe with the queried results on no results.
    """
    time.sleep(1)
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(user_response)
    stop_words = stop_words.union(STOPWORDS_ADD_ON)
    filtered_sentence = []
    p = [',', '.', ':', '?', '!']
    for w in word_tokens:
        if w not in stop_words and w not in p:
            filtered_sentence.append(spell.correction(w))
    # print(word_tokens)
    for roommate_word in ROOMMATES:
        if roommate_word in word_tokens:
            roommate_index = word_tokens.index(roommate_word)
            if word_tokens[roommate_index - 1] in ['no', 'without']:
                new_roommate_word = 'no ' + roommate_word
                if 'without' in filtered_sentence:
                    filtered_sentence.remove('without')
                filtered_sentence.append(spell.correction(new_roommate_word))
                filtered_sentence.remove(spell.correction(roommate_word))
    print(filtered_sentence)
    results = get_user_query(df, filtered_sentence)
    num_of_results = len(results)
    if num_of_results > 0:
        print("RealT: I've found", num_of_results, "posts.")
        time.sleep(1)
        print("RealT: Do you want to see them?")
        user_response = input()
        time.sleep(1)
        if user_response in POSITIVE_INPUTS:
            if num_of_results > 10:
                print("RealT: How much of them do you want to see ? (please type a number)")
                user_response = int(input())
                if user_response < num_of_results:
                    return results.head(user_response)
            return results
        elif user_response in NEGATIVE_INPUTS:
            print("RealT: Ok, anything else to look for? (yes/no)")
            user_response = input()
            time.sleep(1)
            if user_response in NEGATIVE_INPUTS:
                print("RealT: OK, it was a pleasure to help you ! Thanks and have a nice day")
                exit(0)
            else:
                return "what shall i look for?"
        else:
            print("Didn't quite understand")
            user_response = input()
            time.sleep(1)
            if user_response in POSITIVE_INPUTS:
                return results
            elif user_response in NEGATIVE_INPUTS:
                print("RealT: Ok great !, anything else to look for? (yes/no)")
                user_response = input()
                time.sleep(1)
                if user_response in NEGATIVE_INPUTS:
                    print("RealT: OK, it was a pleasure to help you ! Thanks and have a nice day")
                    exit(0)
    else:
        print("Sorry but unfortunately I couldn't find any results")
        time.sleep(1)
        print("RealT: do you want me to look for something else? (yes/no)")
        user_response = input()
        time.sleep(1)
        if user_response in NEGATIVE_INPUTS:
            print("RealT: OK, it was a pleasure to help you ! Thaks and have a nice day")
            exit(0)
        else:
            return "what shall i look for?"


def start_chatbot():
    """
        This Function initiates the conversation with the chatbot,
        its responsible for chatbot responses and gestures, will print result and answers.
        for more complex answers like initiating queries it will start response(user_input) function.
    """
    flag = True
    print("RealT: My name is RealT. \nI am happy and exited to assist you with housing information. \n"
          "Try to ask me about apartments that you are looking for, like - I want a 3 rooms apartment or I want 2 rooms apartment,"
          " with no roommates\nIf you want to exit, you can just type Bye!\nSo lets start and have a lot of fun!")
    while flag:
        user_response = input()
        user_response = user_response.lower().replace('!', '').replace('?','').replace('.','').\
                replace(',','').replace(':','').replace(';','')
        if user_response != 'bye':
            if user_response == 'thanks' or user_response == 'thank you':
                time.sleep(1)
                print("RealT:", random.choice(THANKS_RESPONSES))
                time.sleep(1)
                print("RealT: Any help else to assist with today? (yes/no)")
                user_response = input()
                user_response = user_response.lower()
                if user_response in POSITIVE_INPUTS:
                    print("RealT: What shall i look for?")
                    continue
                elif user_response in NEGATIVE_INPUTS:
                    print("RealT: Have a nice day!")
                    exit(0)
            elif user_response in WHATSAPP:
                time.sleep(1)
                print("RealT:", random.choice(WHATSAPP_RESPONSES))
                time.sleep(1)
                print("RealT: What kind of apartment should i find for you today?")
            elif user_response in TELL_MY_FACT:
                time.sleep(1)
                print("RealT: Listen to that! \n", random.choice(FACTS))
                time.sleep(1)
                print("RealT: Interesting right?!")
                print("RealT: SO now, What kind of apartment should i find for you today?")
            else:
                if user_response in GREETING_INPUTS:
                    time.sleep(1)
                    print("RealT: " + random.choice(GREETING_RESPONSES))
                    time.sleep(1)
                    print("RealT: What kind of apartment should i find for you today?")
                elif user_response in POSITIVE_INPUTS:
                    print("RealT: Great!")
                    time.sleep(1)
                    print("RealT: What kind of apartment should i find for you today?")
                elif user_response in NEGATIVE_INPUTS:
                    print("RealT: Remember that you can exit any time by typing bye!")
                else:
                    time.sleep(1)
                    print("RealT: mmm one sec.")
                    print("RealT: ", end="")
                    # print("Please Elaborate")
                    results = response(user_response)
                    # print("Type:", type(results))
                    if isinstance(results, pd.DataFrame):
                        print("RealT: OK, sure.")
                        posts = results.index.tolist()
                        for post in posts:
                            print("RealT: Post ID:", post)
                            # print(results.loc[post, 'text'])
                            print(results.loc[post, 'post_text'])
                            if str(results.loc[post, 'image']) != 'nan':
                                print("Pic:", results.loc[post, 'image'])
                            if str(results.loc[post, 'post_url']) != 'nan':
                                print("Link:", results.loc[post, 'post_url'])
                            print("")
                            time.sleep(1)
                        print("RealT: That is it! would you like another help?")
                    else:
                        print("RealT:", results)
        else:
            flag = False
            print("RealT: Glad I could assist you today")
            print("RealT: Have a nice day!")


if __name__ == '__main__':
    main()
