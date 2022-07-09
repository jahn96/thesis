from rouge import Rouge


def measure_rouge(reference, candidate):
    # candidate = "the #### transcript is a written version of each day 's cnn student news program use this transcript to he    lp students with reading comprehension and vocabulary use the weekly newsquiz to test your knowledge of storie s you     saw on cnn student news"

    # reference = "this page includes the show transcript use the transcript to help students with reading comprehension and     vocabulary at the bottom of the page , comment for a chance to be mentioned on cnn student news . you must be a teac    her or a student age # # or older to request a mention on the cnn student news roll call . the weekly newsquiz tests     students ' knowledge of even ts in the news"

    rouge = Rouge()
    scores = rouge.get_scores(candidate, reference)

    print(scores)
    return scores

if __name__ == '__main__':
    reference = 'I am on the vacation.'
    candidate = 'I am not on the vacation.'
    measure_rouge(reference, candidate)
