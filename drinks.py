# -*- coding: utf-8 -*-
# Time-stamp: <2014-11-12 13:53:29 moss>

######################################
# Scipt for handling drinks          #
#                                    #
# Made by:  Mads Fabricius Scmidt    #
#           Jakob Rørstes Mosumgaard #
######################################

###########
# Modules #
###########
import codecs
import collections


#####################
# Initial variables #
#####################

# Encoding is always utf8!
ENCODING = 'utf8'

# Name of drinks file defining drinks. Default 'drinks.txt'
drinksfilename = 'drinks.txt'


def readdrinks(drinksfile):
    # Initialize dictories
    drinksdict = collections.OrderedDict()
    secretdrinkdict = collections.OrderedDict()
    currentdrinkdict = None

    # Read the file line by line
    for line in drinksfile:

        # Get the current drink
        if line.startswith('='):
            currentdrinkdict = collections.OrderedDict()

            # Get name of drink without any newline
            currentdrinkname = line.strip('= \n')

            # Sort into secret and normal drinks
            if currentdrinkname.startswith('?'):
                currentdrinkname = currentdrinkname.strip('? ')
                secretdrinkdict[currentdrinkname] = currentdrinkdict
            else:
                drinksdict[currentdrinkname] = currentdrinkdict

        # Soda
        elif line.startswith('--'):
            currentsoda = line.strip(' -\n')

            # Handle multiple soda entries
            if 'soda' in currentdrinkdict:
                currentdrinkdict['soda'].append(currentsoda)
            else:
                currentdrinkdict['soda'] = [currentsoda]

        # Spirit
        elif line.startswith('-'):
            currentspirit = line.strip(' -\n')
            if 'spirit' in currentdrinkdict:
                currentdrinkdict['spirit'].append(currentspirit)
            else:
                currentdrinkdict['spirit'] = [currentspirit]

        # Other
        elif line.startswith('!'):
            currentother = line.strip(' !\n')
            if 'other' in currentdrinkdict:
                currentdrinkdict['other'].append(currentother)
            else:
                currentdrinkdict['other'] = [currentother]

        # Price
        elif line.startswith('$'):
            currentprice = line.strip(' $\n')
            currentdrinkdict['price'] = currentprice

        # This makes sure every other line is ignored.
        # Maybe we should print a warning (with line number)?
        else:
            pass

    return drinksdict, secretdrinkdict


def generatebarcard(drinksdict):
    for drink in drinksdict:
        currentingredients = drinksdict[drink]
        yield r'\drik %s' % drink
        yield r'\til %s' % currentingredients['price']

        # Write every other thing:
        yield r'\med %'

        for spirit in currentingredients['spirit']:
            amount = '\t'
            if '-' in spirit:
                # Split returns an array of strings.
                # amount is the first of these
                amount, spirit = spirit.split('-')
                amount = amount.strip() + '\t'
                spirit = spirit.strip()
            yield r'%s& %s\og' % (amount, spirit)

        for soda in currentingredients['soda']:
            yield '\t\t& %s\\og' % soda

        for other in currentingredients['other']:
            yield '\\serveret I et %s med is\n' % other


#####################################
# The function which does the magic #
#####################################
def makedrinks():
    with codecs.open(drinksfilename, 'r', encoding=ENCODING) as drinksfile:
        drinksdict, secretdrinkdict = readdrinks(drinksfile)

    # Now we make the barcards ("drinkskort").
    # This won't contain the secret drinks.
    # Right now the drinks aren't sorted.
    # The current format of the output is:

    # \section*{name}
    # \begin{itemize}
    # 	\item spirits
    # 	\item sodas
    # 	\item others
    # 	\item price
    # \end{itemize}

    # Write to .tex file. Loop over the number of drinks.
    with codecs.open('barcard.tex', 'w', encoding=ENCODING) as barcard:
        for line in generatebarcard(drinksdict):
            barcard.write('%s\n' % line)

    # Combine and sort the normal and secret drinks.
    drinksdict = collections.OrderedDict(
        list(drinksdict.items()) + list(secretdrinkdict.items()))
    drinksdict_sorted = sorted(drinksdict)

    # Open file for the mixing card ("blandeliste")
    mixingcard = codecs.open('mixing.tex', 'w', encoding=ENCODING)

    # Do TeX-stuff
    mixingcardline = '\\begin{tabular}{lllll}\n'
    mixingcardline += (
        '\\toprule Navn & Sprut & Sodavand & Severing & Pris \\\ \n\midrule')
    mixingcard.writelines(mixingcardline)

    # Loop over all drinks
    drinknumber = 0
    for drink in drinksdict_sorted:
        currentingredients = drinksdict[drink]
        mixingcardline = '{color}{drink} & {ingredients}& '.format(
            color='\\rowcolor{Gray} ' if drinknumber % 2 == 0 else '',
            drink=drink,
            ingredients=', '.join(' '.join(part for part in spirit.split('-'))
                                  for spirit in currentingredients['spirit']),
            )

        # some drinks do not contain any soda,
        # so this check needs to be done beforehand.
        # Maybe this needs to be done before every ingredients?
        for soda in currentingredients.get('soda', []):
            mixingcardline += soda + ' '
        mixingcardline += '& '
        for other in currentingredients['other']:
            mixingcardline += other + ' '
        mixingcardline += '& '
        mixingcardline += currentingredients['price'] + ' kr\\\ \n'
        mixingcard.writelines(mixingcardline)
        drinknumber += 1
    mixingcardline = '\\bottomrule\n\end{tabular}'
    mixingcard.writelines(mixingcardline)
    mixingcard.close()

    # Wuhu! Done!


# Run the function if file is called directly
if __name__ == '__main__':
    makedrinks()
