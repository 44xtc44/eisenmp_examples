"""Module runs aacrepair on commandline with menu options.

Please check ``error_dict`` message, if instance fails to repair.
"""
import eisenmp_examples


def menu_main():
    """Main menu to choose from."""

    exit_msg = '\n  Thank you for using eisenmp_examples.'
    option_msg = 'Invalid option. Please enter a number between 1 and 8.'

    print('\n\tMenu "Example"\n')
    menu_options_dict = {
        1: 'Three processes, multiple Flask server in each - share a DB',
        2: 'Each CPU, one Flask server on each - share a DB',
        3: 'Prime Number calculation',
        4: 'Web CSV large list calculation',
        5: 'Each CPU, one simple http server presents a radio',
        6: 'Two Queues fed at once',
        7: 'Brute force attack with dictionary and itertools generator',
        8: 'Exit',
    }

    while 1:
        for key in menu_options_dict.keys():
            print(key, '--', menu_options_dict[key])
        try:
            option = int(input('Enter your choice: '))
        except ValueError:
            print(option_msg)
            continue
        if option == 1:
            eisenmp_examples.eisenmp_exa_multi_srv_each_cpu.main()
            break
        elif option == 2:
            eisenmp_examples.eisenmp_exa_each_flask_orm_srv_one_cpu.main()
            break
        elif option == 3:
            eisenmp_examples.eisenmp_exa_prime.main()
            break
        elif option == 4:
            eisenmp_examples.eisenmp_exa_web_csv.main()
            break
        elif option == 5:
            eisenmp_examples.eisenmp_exa_http.main()
            break
        elif option == 6:
            eisenmp_examples.eisenmp_exa_double_q.main()
            break
        elif option == 7:
            eisenmp_examples.eisenmp_exa_bruteforce.main()
            break

        elif option == 8:
            print(exit_msg)
            exit()
        else:
            print(option_msg)
    return


def main():
    """Call menu_main to start the module from command line."""
    menu_main()


if __name__ == '__main__':
    main()
