class Result:
    def __init__(self, first, second, third, fourth, fifth):
        self.results = [first, second, third, fourth, fifth]
        self.result = self.average()

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
        self.best_solve = self.best(results_in_sec)
        if not DNFs :
            total = total - self.best_solve - self.worst(results_in_sec)
            return str(round(total/3, 2))
        elif DNFs < 2:
            total = total - self.best_solve
            return str(round(total/3, 2))
        else:
            return str('999')

    def formated(self, time):#returning str representing avg in mm:ss.ff
        print(time)
        if time == '999':
            return 'DNF'
        minutes = int(float(time)/60)
        seconds = round(float(time) - minutes*60, 2)
        print(minutes, seconds, float(time)-minutes*60)
        if minutes:
            return(f'{minutes}:{seconds}')
        return(str(seconds))
    
        


if __name__ == '__main__':
    a = Result('54.00', '47.93', '59.11', '53.70', '55.20')
    b = a.average()
    c = a.formated(b)
    print(a.best_solve, b, c)