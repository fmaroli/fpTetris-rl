import torch
from environment.tetris import Tetris

width = 10
height = 20
block_m = 30
saved_path = "models"

def test():

    if torch.cuda.is_available():
        torch.cuda.manual_seed(123)
    else:
        torch.manual_seed(123)
    if torch.cuda.is_available():
        model = torch.load("{}/tetris_lines115867_epoch2528".format(saved_path))
    else:
        model = torch.load("{}/tetris".format(saved_path), map_location=lambda storage, loc: storage)
    model.eval()
    env = Tetris(width=width, height=height, block_m=block_m)
    env.restart()
    if torch.cuda.is_available():
        model.cuda()
    while True:
        next_steps = env.get_nxt_state()
        next_actions, next_states = zip(*next_steps.items())
        next_states = torch.stack(next_states)
        if torch.cuda.is_available():
            next_states = next_states.cuda()
        predictions = model(next_states)[:, 0]
        index = torch.argmax(predictions).item()
        action = next_actions[index]
        _, done = env.step(action, render=True)

        if done:
            break

if __name__ == "__main__":
    test()
