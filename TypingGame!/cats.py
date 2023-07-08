"""Typing test implementation"""

from utils import lower, split, remove_punctuation, lines_from_file
from ucb import main, interact, trace
from datetime import datetime


###########
# Phase 1 #
###########


def choose(paragraphs, select, k):
    """Return the Kth paragraph from PARAGRAPHS for which SELECT called on the
    paragraph returns True. If there are fewer than K such paragraphs, return
    the empty string.
    """
    new_para_list = [word for word in paragraphs if select(word)]
    return '' if len(new_para_list) < k + 1 else new_para_list[k]

def about(topic):
    """Return a select function that returns whether
    a paragraph contains one of the words in TOPIC.

    Arguments:
        topic: a list of words related to a subject
    """
    assert all([lower(x) == x for x in topic]), 'topics should be lowercase.'
    def select(paragraph):
        formatted_paragraph = remove_punctuation(paragraph).lower().split()
        for words in topic:
            for word in formatted_paragraph:
                if words == word:
                    return True
        return False
    return select

def accuracy(typed, reference):
    """Return the accuracy (percentage of words typed correctly) of TYPED
    when compared to the prefix of REFERENCE that was typed.
    """
    typed_words = split(typed)
    reference_words = split(reference)
    k = 0
    score = 0.0
    if len(typed_words) == 0 and len(reference_words) == 0:
        return 100.0
    elif len(typed_words) == 0:
        return 0.0
    for words, comp_words in zip(typed_words, reference_words):
        if words == comp_words:
            k += 1
    score = k / len(typed_words)
    return score * 100

def wpm(typed, elapsed):
    """Return the words-per-minute (WPM) of the TYPED string.
    """
    assert elapsed > 0, 'Elapsed time must be positive'
    return len(typed) / 5 * 60 / elapsed

def autocorrect(typed_word, word_list, diff_function, limit):
    """Returns the element of WORD_LIST that has the smallest difference
    from TYPED_WORD. Instead returns TYPED_WORD if that difference is greater
    than LIMIT.
    """
    if typed_word in word_list:
        return typed_word
    pairs = {word : diff_function(typed_word, word, limit) for word in word_list}
    if min(pairs.values()) <= limit:
        # returns the key value in a dictionary where the value is the smallest
        return min(pairs, key = lambda i: pairs[i])
    else:
        return typed_word

def sphinx_swaps(start, goal, limit):
    """A diff function for autocorrect that determines how many letters
    in START need to be substituted to create GOAL, then adds the difference in
    their lengths and returns the result.
    """
    diff = 0
    if start == goal:
        return 0
    if limit == 0:
        return 1
    if min(len(start), len(goal)) == 0:
        return max(len(start),len(goal))
    if start[0] != goal[0]:
        diff += 1
    return diff + sphinx_swaps(start[1:],goal[1:],limit - diff)

def minimum_mewtations(start, goal, limit):
    """A diff function that computes the edit distance from START to GOAL.
    This function takes in a string START, a string GOAL, and a number LIMIT.
    """
    diff = 0
    if limit < 0:
        return 1
    elif start == goal:
        return 0
    elif min(len(start), len(goal)) == 0:
        return max(len(start), len(goal))
    else:
        if start[0] != goal[0]:
            diff += 1
        add = 1 + minimum_mewtations(start, goal[1:], limit - 1)
        remove = 1 + minimum_mewtations(start[1:], goal, limit - 1)
        substitute = diff + minimum_mewtations(start[1:], goal[1:], limit - diff)
    return min(add, remove, substitute)

def final_diff(start, goal, limit):
    """A diff function that takes in a string START, a string GOAL, and a number LIMIT.
    If you implement this function, it will be used."""
    assert False


FINAL_DIFF_LIMIT = 6  # REPLACE THIS WITH YOUR LIMIT

def report_progress(sofar, prompt, user_id, upload):
    """Upload a report of your id and progress so far to the multiplayer server.
    Returns the progress so far.

    Arguments:
        sofar: a list of the words input so far
        prompt: a list of the words in the typing prompt
        user_id: a number representing the id of the current user
        upload: a function used to upload progress to the multiplayer server
    """
    i = 1
    while i <= len(sofar) and sofar[:i] == prompt[:i]:
        i += 1
    progress = (i-1)/len(prompt)
    upload_content = {'id':user_id, 'progress':progress}
    upload(upload_content)
    return progress

def time_per_word(words, times_per_player):
    """Given timing data, return a match dictionary, which contains a
    list of words and the amount of time each player took to type each word.

    Arguments:
        words: a list of words, in the order they are typed.
        times_per_player: A list of lists of timestamps including the time
                          the player started typing, followed by the time
                          the player finished typing each word.
    """
    for time in times_per_player:
        for i in range(len(time)-1):
            times = [[time[i+1] - time[i]]]
    return match(words, times)


def fastest_words(match):
    """Return a list of lists of which words each player typed fastest.

    Arguments:
        match: a match dictionary as returned by time_per_word.
        """
    player_indices = range(len(match["times"]))  # contains an *index* for each player
    word_indices = range(len(match["words"]))    # contains an *index* for each word
    answers = [[] for ans in player_indices]
    for word in word_indices:
        times = [time(match, i, word) for i in player_indices]
        answers[time.index(min(times))].append(word_at(match, word))
    return answers


def match(words, times):
    """A dictionary containing all words typed and their times.

    Arguments:
        words: A list of strings, each string representing a word typed.
        times: A list of lists for how long it took for each player to type
            each word.
            times[i][j] = time it took for player i to type words[j].

    Example input:
        words: ['Hello', 'world']
        times: [[5, 1], [4, 2]]
    """
    assert all([type(w) == str for w in words]), 'words should be a list of strings'
    assert all([type(t) == list for t in times]), 'times should be a list of lists'
    assert all([isinstance(i, (int, float)) for t in times for i in t]), 'times lists should contain numbers'
    assert all([len(t) == len(words) for t in times]), 'There should be one word per time.'
    return {"words": words, "times": times}


def word_at(match, word_index):
    """A utility function that gets the word with index word_index"""
    assert 0 <= word_index < len(match["words"]), "word_index out of range of words"
    return match["words"][word_index]


def time(match, player_num, word_index):
    """A utility function for the time it took player_num to type the word at word_index"""
    assert word_index < len(match["words"]), "word_index out of range of words"
    assert player_num < len(match["times"]), "player_num out of range of players"
    return match["times"][player_num][word_index]


def match_string(match):
    """A helper function that takes in a match dictionary and returns a string representation of it"""
    return f"match({match['words']}, {match['times']})"


enable_multiplayer = False  # Change to True when you're ready to race.

##########################
# Command Line Interface #
##########################


def run_typing_test(topics):
    """Measure typing speed and accuracy on the command line."""
    paragraphs = lines_from_file('data/sample_paragraphs.txt')
    select = lambda p: True
    if topics:
        select = about(topics)
    i = 0
    while True:
        reference = choose(paragraphs, select, i)
        if not reference:
            print('No more paragraphs about', topics, 'are available.')
            return
        print('Type the following paragraph and then press enter/return.')
        print('If you only type part of it, you will be scored only on that part.\n')
        print(reference)
        print()

        start = datetime.now()
        typed = input()
        if not typed:
            print('Goodbye.')
            return
        print()

        elapsed = (datetime.now() - start).total_seconds()
        print("Nice work!")
        print('Words per minute:', wpm(typed, elapsed))
        print('Accuracy:        ', accuracy(typed, reference))

        print('\nPress enter/return for the next paragraph or type q to quit.')
        if input().strip() == 'q':
            return
        i += 1


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Typing Test")
    parser.add_argument('topic', help="Topic word", nargs='*')
    parser.add_argument('-t', help="Run typing test", action='store_true')

    args = parser.parse_args()
    if args.t:
        run_typing_test(args.topic)
