# Step 1
## Computing the spreading of a disease inside a single group of people
Given the formula:

$$ S(t)+I(t)+R(t)=N $$

Where:
- $$ N $$ is the total number of people
- $$ S $$ is the number of susceptible people
- $$ I $$ is the number of infected
- $$ R $$ is the number of recovered

The corresponding formula identified by the lower letter is equal to the proportion of population in the corresponding state. Consequently:

$$ s(t)+i(t)+r(t)=1 $$


// TODO: check it, I'm not sure about it
$$ R_0(t)=\beta s(t) i(t) - \gamma i(t) $$

The $$ R_0 $$ can be computed with the formula:

$$ R_0(t) = \frac{ \beta }{ \gamma } $$

The delta in the RSI model is given by:

$$ \delta s = - \beta s i $$

$$ \delta i = \beta s i - \gamma i $$

$$ \delta r = \gamma i $$

## Source:
- https://calculate.org.au/wp-content/uploads/sites/15/2018/10/spread-of-disease.pdf