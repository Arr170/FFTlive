class Result:
    def __init__(self, first, second, third, fourth, fifth):
        self.first = first
        self.second = second
        self.third = third
        self.fourth = fourth
        self.fifth = fifth
        self.results = [first, second, third, fourth, fifth]

    def best(self, results_in_sec):
        best = 600
        for result in results_in_sec:
            #print(type(num), num)
            if result == float(0):
                None
            else:
                if result < best:
                    best = result
        return(best)
    
    def worst(self, results_in_sec):
        worst = 0
        for result in results_in_sec:
                if result > worst:
                    worst = result
        return(worst)

    def average(self):#returns time in seconds.milliseconds
        results_in_sec = []#storing results in seconds (float type)
        total = 0#storing total time of 5 solves
        DNFs = 0
        for result in self.results:
            if result == 'DNF':
                DNFs += 1
                results_in_sec.append(float(0))
            else:
                min = result[-7:-6]
                sec = result[-5:]
                if min:
                    solve = float(min)*60 + float(sec)
                    total += solve
                    results_in_sec.append(solve)
                else:
                    solve = float(sec)
                    total += solve
                    results_in_sec.append(solve)
        if DNFs < 2 :
            total = total - self.best(results_in_sec) - self.worst(results_in_sec)
            return str(self.truncate(total/3, 2))
        else:
            return str('DNF')

    def to_string(self, time):
        if time == 'DNF':
            return 'DNF'
        minutes = int(float(time)/60)
        seconds = float(time) - minutes*60
        if minutes:
            return(f'{minutes}:{seconds}')
        return(str(seconds))
    
    def truncate(self, n, decimals=0):
        multiplier = 10 ** decimals
        return int(n * multiplier) / multiplier

        


if __name__ == '__main__':
    a = Result('1:00.00', '3:00.00', '2:22.00', '34.34', '11.11')
    b = a.average()
    c = a.to_string(b)
    print('a',len(c))