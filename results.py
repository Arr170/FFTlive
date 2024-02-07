class Result:
    def __inti(self, first, second, third, fourth, fifth):
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

    def average(self):
        results_in_sec = []#storing results in seconds (float type)
        total = 0#storing total time of 5 solves
        DNFs = 0
        for result in self.results:
            if result == 'DNF':
                DNFs += 1
                results_in_sec.append(float(0))
            else:
                millisec = result[-2:]
                sec = result[-5:-3]
                min = result[-7:-6]
                if min:
                    solve = float(min) + float(sec) + float(millisec)/100
                    total += solve
                    results_in_sec.append(solve)
                else:
                    solve = float(sec) + float(millisec)/100
                    total += solve
                    results_in_sec.append(solve)
        if DNFs < 2 :
            total = total - self.best(results_in_sec) - self.worst(results_in_sec)
            return str(total/3)
        else:
            return str('DNF')

