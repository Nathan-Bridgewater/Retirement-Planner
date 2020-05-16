"""A Monte Carlo simulation for estimating the probability of running out
of money in retirement. Years in retirement are treated as an uncertainty,
the simulation uses historical stock, bond and and inflation data to capture
the interdependency of the variables."""
import sys
import random
import matplotlib.pyplot as plt


def read_to_list(file_name):
    """Open a file of data in percent, convert to decimal and return a list."""
    with open(file_name) as in_file:
        # loop through each line, convert to float and then decimal
        lines = [float(line.strip()) for line in in_file]
        decimal = [round(line / 100, 5) for line in lines]
        return decimal


def default_input(prompt, default=None):
    """Allow use of default values as input."""
    # display input question and default answer
    prompt = f"{prompt} [{default}]"
    response = input(prompt)

    if not response and default:
        # user chooses to use default value
        return default

    else:
        # user chooses their own value
        return response


# load data files with original data in percent form
print("\nNote: input data should be in percent not decimal.\n")

try:
    # load in returns for various types of investment and inflation data
    bonds = read_to_list('10-yr_TBond_returns_1926-2013_pct.txt')
    stocks = read_to_list('SP500_returns_1926-2013_pct.txt')
    blend_40_50_10 = read_to_list('S-B-C_blend_1926-2013_pct.txt')
    blend_50_50 = read_to_list('S-B_blend_1926-2013_pct.txt')
    infl_rate = read_to_list('annual_infl_rate_1926-2013_pct.txt')

except IOError as e:
    print(f"{e}. Terminating program.", file=sys.stderr)

# get user input; use dictionary for investment type arguments
investment_type_args = {'bonds': bonds, 'stocks': stocks,
                        'sb_blend': blend_50_50, 'sbc_blend': blend_40_50_10}

# print input legend for user
print("    stocks = SP500")
print("     bonds = 10-yr- Treasury Bond")
print("  sb_blend = 50% SP500/50% TBond")
print(" sbc_blend = 40% SP500/ 50% TBond/ 10% Cash\n")

print("Press ENTER to take default value shown in [brackets]. \n")

# get user input
invest_type = default_input("Enter investment type: (stocks, bonds, sb_blend,"
                            " sbc_blend): ", default='bonds')

# ensure user enters a valid investment type
while invest_type not in investment_type_args:
    invest_type = input("Invalid investment type. Enter investment listed: ")

# get value of users investments at start of retirement
start_value = default_input("Input starting value of investments: \n",
                            '2000000')

while not start_value.isdigit():  # ensure number
    start_value = input('Invalid input. Please enter an integer value: ')

# get value of users average yearly out's pre tax
withdrawal = default_input("Input annual pre-tax withdrawal"
                           " (today's $): \n", default='80000')
while not withdrawal.isdigit():  # ensure number
    withdrawal = input('Invalid input. Please enter an integer value: ')

# get minimum, most likely and maximum years expected in retirement
min_years = default_input("Input minimum years in retirement: \n", '18')
while not min_years.isdigit():
    min_years = input('Invalid input. Please enter an integer value: ')

most_likely_years = default_input("Input most likely years in retirement: \n",
                                  '25')
while not most_likely_years.isdigit():
    most_likely_years = input('Invalid input. Please enter an integer value.')

max_years = default_input("Input maximum years in retirement: \n", '40')
while not max_years.isdigit():
    max_years = input('Invalid input. Please enter an integer value.')

num_cases = default_input("Input number of cases to run: \n", '50000')
while not num_cases.isdigit():
    num_cases = input('Invalid input. Please enter an integer value')

# check for erroneous input
if not int(min_years) < int(most_likely_years) < int(max_years) \
        or int(max_years) > 99:
    print("\nProblem with input years.", file=sys.stderr)
    print("Requires Min < ML < Max with Max < 99")
    sys.exit(1)


def montecarlo(returns):
    """Run MCS and return investment value at end-of-plan and bankrupt count."""
    # track which case, number of bankruptcies, outcome of each run
    case_count = 0
    bankrupt_count = 0
    outcome = []

    # loop through a set number of cases
    while case_count < int(num_cases):
        investments = int(start_value)
        # pick a start value from the range of available years
        start_year = random.randrange(0, len(returns))
        # randomly pick duration from triangular distribution
        duration = int(random.triangular(int(min_years), int(max_years),
                                         int(most_likely_years)))

        end_year = start_year + duration
        lifespan = [i for i in range(start_year, end_year)]
        bankrupt = 'no'

        # build temporary lists for each case
        lifespan_returns = []
        lifespan_infl = []
        for i in lifespan:
            # if the lifespan index is out of the range of returns/infl
            # then wrap the list and start at the beginning
            lifespan_returns.append(returns[i % len(returns)])
            lifespan_infl.append(infl_rate[i % len(infl_rate)])

        # loop through each year of retirement for each case to run
        for index, i in enumerate(lifespan_returns):
            infl = lifespan_infl[index]

            # dont adjust for inflation in the first year
            if index == 0:
                withdraw_inf_adj = int(withdrawal)

            else:
                # adjust withdrawal amount to match inflation
                withdraw_inf_adj = int(withdraw_inf_adj * (1 + infl))

            # calculate new investments value
            investments -= withdraw_inf_adj
            investments = int(investments * (1 + i))

            if investments <= 0:  # end when bankrupt
                bankrupt = 'yes'
                break

        if bankrupt == 'yes':
            # set outcome to 0 and add a count for bankruptcy
            outcome.append(0)
            bankrupt_count += 1

        else:
            outcome.append(investments)

        case_count += 1

    return outcome, bankrupt_count


def bankrupt_prob(outcome, bankrupt_count):
    """Calculate and return chance of running out od money & other stats"""
    total = len(outcome)
    odds = round(100 * bankrupt_count / total, 1)

    # display information in terminal
    print(f"\nInvestment type: {invest_type}")
    print(f"Starting value: {int(start_value):,}")
    print(f"Annual withdrawal: ${int(withdrawal):,}")
    print(f"Years in retirement (min-ml-max): {min_years}-{most_likely_years}"
          f"-{max_years}")
    print(f"Number of runs: {total:,}\n")
    print(f"Odds of running out of money: {odds}%")
    print(f"Average outcome: ${int(sum(outcome) / total):,}")
    print(f"Minimum outcome: ${(min(i for i in outcome)):,}")
    print(f"Maximum outcome: ${(max(i for i in outcome)):,}")

    return odds


def main():
    """Call MCS and bankrupt functions and draw bar chart of results."""
    outcome, bankrupt_count = montecarlo(investment_type_args[invest_type])
    odds = bankrupt_prob(outcome, bankrupt_count)

    # plot a bar chart of the data
    plotdata = outcome[:3000]  # only plot first 3000 runs
    plt.figure(f'Outcome by Case (showing first {len(plotdata)} runs',
               figsize=(16, 5))  # size is width/ height in inches
    index = [i + 1 for i in range(len(plotdata))]
    plt.bar(index, plotdata, color='black')
    plt.xlabel('Simulated Lives', fontsize=18)
    plt.ylabel('$ remaining', fontsize=18)
    plt.ticklabel_format(style='plain', axis='y')
    plt.title(f'Probability of running out of money = {odds}%',
              fontsize=20, color='red')
    plt.show()

    # run program


if __name__ == '__main__':
    main()