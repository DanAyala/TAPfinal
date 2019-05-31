def mixedMethod(x, a, c, mod):
    periodo = 0
    bandera = 0

    while (bandera != x):
        if (periodo == 0):
            bandera = x
        x = (a * x + c) % mod
        print(x)
        periodo = periodo + 1

    if (periodo == mod):
        print("El periodo es completo: ", periodo)
    else:
        print("El periodo es incompleto:", periodo)


def main():
    x = int(input("Introduce el valor de la semilla x: "))
    a = int(input("Introduce el valor del multiplicador a : "))
    c = int(input("Introduce el valor de la constante aditiva c: "))
    m = int(input("Introduce el valor del modulo m: "))
    mixedMethod(x, a, c, m)


if __name__ == "__main__":
    main()