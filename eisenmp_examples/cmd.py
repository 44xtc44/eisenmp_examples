"""commandline menu for eisenmp_examples

manifest del __pycache__
flask collision with existing version in eisenradio
rename http server to url.py
    start browser auto
write docu and user menu pypi in color
    python -m eisenmp_examples.cmd  commandline menu
    python -m eisenmp_examples.url  ajax http server
"""
import eisenmp_examples.eisenmp_exa_multi_srv_each_cpu as multi_srv_each_cpu
import eisenmp_examples.eisenmp_exa_each_flask_orm_srv_one_cpu as flask_orm_srv_one_cpu
import eisenmp_examples.eisenmp_exa_prime as prime
import eisenmp_examples.eisenmp_exa_web_csv as web_csv
import eisenmp_examples.eisenmp_exa_http as http
import eisenmp_examples.eisenmp_exa_double_q as double_q
import eisenmp_examples.eisenmp_exa_bruteforce as bruteforce
import eisenmp_examples.url as frontend


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
        8: '   ### Ajax Frontend, open browser to click examples ###',
        9: 'Exit',
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
            multi_srv_each_cpu.main()
            break
        elif option == 2:
            flask_orm_srv_one_cpu.main()
            break
        elif option == 3:
            prime.main()
            break
        elif option == 4:
            web_csv.main()
            break
        elif option == 5:
            http.main()
            break
        elif option == 6:
            double_q.main()
            break
        elif option == 7:
            bruteforce.main()
            break
        elif option == 8:
            frontend.main()
            break
        elif option == 9:
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
