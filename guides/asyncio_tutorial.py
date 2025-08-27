import asyncio

async def task(name, delay):
    await asyncio.sleep(delay)
    print(f"{name} done after {delay}s")
    return name

async def main():
    results = await asyncio.gather(
        task("A", 1),
        task("B", 2),
        task("C", 3)
    )
    print(results)

async def fetch_data():
    await asyncio.sleep(1)
    print("Fetched Data")
    return "Fetched Data."

async def process_data():
    await asyncio.sleep(1)
    print("Processed Data")
    return "Processed Data."

async def save_data():
    await asyncio.sleep(1)
    print("Saved Data")
    return "Saved Data"

async def countdown(seconds):
    while seconds > 0:
        print(f"Countdown: {seconds}")
        await asyncio.sleep(1)
        seconds -= 1
    print("Done")    

async def greet(name, name2, name3):
    await asyncio.sleep(1)
    return f"Hello {name} {name2} {name3}!"

import gradio as gr

gr.Interface(fn=greet, inputs=["text", "text", "text"], outputs="text").launch()

# async def main():
#     results = await asyncio.gather(
#         fetch_data(),
#         process_data(),
#         save_data()
#     )
#     print(results)

# asyncio.run(countdown(5))
