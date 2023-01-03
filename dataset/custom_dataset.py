import torch
from torch.utils.data import Dataset
from torch.utils.data import DataLoader # wrapper for iterables over dataset

import numpy as np

class CustomDataset(Dataset):
    def __init__(self, problem, reduced_problem, N):
        '''
        problem: FEM problem with attibutes:
            solve: method to compute full order model solution
        reduced_problem: reduced problem with attributes:
            project_snapshot: Project FEM solution on the reduced basis space
            input_scaling_range: (2,num_para) np.ndarray, row 0 are the SCALED INPUT min_values and row 1 are the SCALED INPUT max_values
            output_scaling_range: (2,num_para) np.ndarray, row 0 are the SCALED OUTPUT min_values and row 1 are the SCALED OUTPUT max_values
            input_range: (2,num_para) np.ndarray, row 0 are the ACTUAL INPUT min_values and row 1 are the ACTUAL INPUT max_values
            output_range: (2,num_para) np.ndarray, row 0 are the ACTUAL OUTPUT min_values and row 1 are the ACTUAL OUTPUT max_values
            input_file_path: Path to ACTUAL INPUT file (numpy array)
        N: int, size of reduced basis
        '''
        assert hasattr(reduced_problem,"input_range")
        assert hasattr(reduced_problem,"input_scaling_range")
        assert hasattr(reduced_problem,"output_range")
        assert hasattr(reduced_problem,"output_scaling_range")
        assert hasattr(reduced_problem,"input_file_path")
        assert hasattr(reduced_problem,"project_snapshot")
        assert hasattr(problem,"solve")
        self.problem = problem
        self.reduced_problem = reduced_problem
        self.N = N
        
    def __len__(self):
        return np.load(self.reduced_problem.input_file_path).shape[0]
    
    def __getitem__(self,idx):
        input_data = np.load(self.reduced_problem.input_file_path)[idx,:]
        label = self.reduced_problem.project_snapshot(self.problem.solve(input_data),self.N)#.array
        return self.transform(input_data), self.target_transform(label)
            
    def transform(self, input_data):
        input_data_scaled = (self.reduced_problem.input_scaling_range[1] - self.reduced_problem.input_scaling_range[0]) * (input_data - self.reduced_problem.input_range[0,:]) / (self.reduced_problem.input_range[1,:] - self.reduced_problem.input_range[0,:]) + self.reduced_problem.input_scaling_range[0]
        return torch.from_numpy(input_data_scaled)
    
    def target_transform(self,label):
        output_data_scaled = (self.reduced_problem.output_scaling_range[1] - self.reduced_problem.output_scaling_range[0]) * (label - self.reduced_problem.output_range[0]) / (self.reduced_problem.output_range[1] - self.reduced_problem.output_range[0]) + self.reduced_problem.output_scaling_range[0]
        return torch.from_numpy(output_data_scaled)
    
    def reverse_transform(self, input_data_scaled): # TODO verify formula
        input_data_scaled = input_data_scaled.detach().numpy()
        input_data = (input_data_scaled - self.reduced_problem.input_scaling_range[0]) * (self.reduced_problem.input_range[1,:] - self.reduced_problem.input_range[0,:]) / (self.reduced_problem.input_scaling_range[1] - self.reduced_problem.input_scaling_range[0]) + self.reduced_problem.input_range[0,:]
        return input_data
    
    def reverse_target_transform(self,output_data_scaled):# TODO verify formula
        output_data_scaled = output_data_scaled.detach().numpy()
        output_data = (output_data_scaled - self.reduced_problem.output_scaling_range[0]) * (self.reduced_problem.output_range[1] - self.reduced_problem.output_range[0]) / (self.reduced_problem.output_scaling_range[1] - self.reduced_problem.output_scaling_range[0]) + self.reduced_problem.output_range[0]
        return output_data

'''
class ReducedProblem(object):
    def __init__(self):
        super().__init__()
        para_dim = 17
        self.input_range = np.vstack((np.zeros([1,para_dim]),np.ones([1,para_dim])))
        self.input_scaling_range = [0.,1.]
        self.output_range = [0.,3.]
        self.output_scaling_range = [0.,1.]
        self.input_file_path = "input_data.npy"
    def project_snapshot(self,fem_solution, N):
        if fem_solution.shape[0] >=N:
            return fem_solution[:N]
        else:
            return fem_solution

class Problem(object):
    def __init__(self):
        super().__init__()
    def solve(self,input_para):
        return np.hstack((2. * input_para, 3. * input_para))

input_data = np.random.uniform(0.,1.,[100,17])
np.save("input_data.npy",input_data)

problem = Problem()
reduced_problem = ReducedProblem()
N = 2

customDataset = CustomDataset(problem, reduced_problem, N)

train_dataloader = DataLoader(customDataset, batch_size=1, shuffle=False)
test_dataloader = DataLoader(customDataset, batch_size=1)

for X, y in train_dataloader:
    print(f"Shape of training set: {X.shape}")
    print(f"Training set requires grad: {X.requires_grad}")
    #print(f"X: {X}")
    print(f"Shape of training set: {y.shape}")
    print(f"Training set requires grad: {y.requires_grad}")
    #print(f"y: {y}")
    break

for X,y in test_dataloader:
    print(f"Shape of test set: {X.shape}")
    print(f"Testing set requires grad: {X.requires_grad}")
    #print(f"X: {X}")
    print(f"Shape of test set: {y.shape}")
    print(f"Testing set requires grad: {y.requires_grad}")
    #print(f"y: {y}")
    break
'''
