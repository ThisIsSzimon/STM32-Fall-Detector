data = readtable('data/nowe_dane.csv');

X = data{:,1};
Y = data{:,2};
Z = data{:,3};

A = sqrt(X.^2 + Y.^2 + Z.^2);

figure(2);
plot(A, 'k');
title('Moduł przyspieszenia A = sqrt(X^2 + Y^2 + Z^2)');
xlabel('Próbki');
ylabel('A [m/s^2]');
grid on;