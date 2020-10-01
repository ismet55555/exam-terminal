import textwrap

sample_text = "fasdfsa' f sf af asfsadfsadfas as sdf asfsdf sdafsadfs s sa fsadf sadfsadasfdsadfsd f  sdfasd fsd"


# Wrap this text. 
wrapper = textwrap.TextWrapper(width=20) 

word_list = wrapper.wrap(text=sample_text) 
  
# Print each line. 
for i, element in enumerate(word_list): 
    print(i, element) 