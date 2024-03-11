import shutil
from random import random, randint, sample
import os
import torch.nn as nn
import torch
from tensorboardX import SummaryWriter
import numpy as np
from environment.tetris import Tetris
from collections import deque
from dqn.dqn import CustomDeepQNetwork

width = 10
height = 20
block_m = 30
batch_size = 512
learning_rate = 1e-3
gamma = 0.99
start_epsilon = 1
end_epsilon = 1e-3
n_decay_epochs = 2000
n_epochs = 3000
replay_mem_size = 30000
logs_path = "tensorboard"
saving_path = "models"

def train():
    if torch.cuda.is_available():
        torch.cuda.manual_seed(2846)
    else:
        torch.manual_seed(2846)
    if os.path.isdir(logs_path):
        shutil.rmtree(logs_path)
    os.makedirs(logs_path)
    tbwriter = SummaryWriter(logs_path)
    environment = Tetris(width=width, height=height, block_m=block_m)
    model = CustomDeepQNetwork()
    optimiser = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criter = nn.MSELoss()

    state = environment.restart()
    if torch.cuda.is_available():
        model.cuda()
        state = state.cuda()

    replay_mem = deque(maxlen=replay_mem_size)
    epoch = 0
    while epoch < n_epochs:
        next_steps = environment.get_nxt_state()
        # Exploration or exploitation
        epsilon = end_epsilon + (max(n_decay_epochs - epoch, 0) * (
                start_epsilon - end_epsilon) / n_decay_epochs)
        u_rand = random()
        random_action = u_rand <= epsilon
        next_actions, next_states = zip(*next_steps.items())
        next_states = torch.stack(next_states)
        if torch.cuda.is_available():
            next_states = next_states.cuda()
        model.eval()
        with torch.no_grad():
            predictions = model(next_states)[:, 0]
        model.train()
        if random_action:
            index = randint(0, len(next_steps) - 1)
        else:
            index = torch.argmax(predictions).item()

        sel_state = next_states[index, :]
        action = next_actions[index]

        reward, done = environment.step(action, render=False)

        if torch.cuda.is_available():
            sel_state = sel_state.cuda()
        replay_mem.append([state, reward, sel_state, done])
        if done:
            final_points = environment.points
            final_pieces = environment.pieces
            final_lines_cleared = environment.lines_cleared
            state = environment.restart()
            if torch.cuda.is_available():
                state = state.cuda()
        else:
            state = sel_state
            continue
        if len(replay_mem) < replay_mem_size / 10:
            continue
        epoch += 1
        batch = sample(replay_mem, min(len(replay_mem), batch_size))
        state_batch, reward_batch, next_state_batch, done_batch = zip(*batch)
        state_batch = torch.stack(tuple(state for state in state_batch))
        reward_batch = torch.from_numpy(np.array(reward_batch, dtype=np.float32)[:, None])
        next_state_batch = torch.stack(tuple(state for state in next_state_batch))

        if torch.cuda.is_available():
            state_batch = state_batch.cuda()
            reward_batch = reward_batch.cuda()
            next_state_batch = next_state_batch.cuda()

        q_values = model(state_batch)
        model.eval()
        with torch.no_grad():
            next_prediction_batch = model(next_state_batch)
        model.train()

        y_batch = torch.cat(
            tuple(reward if done else reward + gamma * prediction for reward, done, prediction in
                  zip(reward_batch, done_batch, next_prediction_batch)))[:, None]

        optimiser.zero_grad()
        loss = criter(q_values, y_batch)
        loss.backward()
        optimiser.step()

        print("Epoch: {}/{}, Action: {}, Score: {}, Tetrominoes {}, Cleared lines: {}".format(
            epoch,
            n_epochs,
            action,
            final_points,
            final_pieces,
            final_lines_cleared))
        tbwriter.add_scalar('Points x Epoch', final_points, epoch - 1)
        tbwriter.add_scalar('Tetrominoes placed x Epoch', final_pieces, epoch - 1)
        tbwriter.add_scalar('Lines Cleared x Epoch', final_lines_cleared, epoch - 1)

        if final_lines_cleared >= 1000:
            torch.save(model, "{}/tetris_lines{}_epoch{}".format(saving_path, final_lines_cleared, epoch))

    torch.save(model, "{}/tetris".format(saving_path))


if __name__ == "__main__":
    train()
