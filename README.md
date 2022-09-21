# shared_utilities
a place for HuMoNs to share generally helpful code with other HuMoNs

## 2022-09-21 - post-processing freemocap data for BOS/COM analysis
1. get yrself a `freemocap` session with 3d data
2. run `freemocap_post_processing_jupyter_notebooks/freemocap_filter_and_origin_align_runme.ipynb`
  - adapt `session_id` and `freemocap_data_path` and whatnot appropriately for your computer/session
3. run `freemocap_post_processing_jupyter_notebooks/export_freemocap_npy_as_pandas_data_frame_csv.ipynb`
  - again altering paths and stuff
4. run `pre-alpha` freemocap on that session with `useBlender` set to `True` to get a gravity aligned blender skeleton
  - May need to re-run 2-3 with better `good_frame` specified manually
  - May need to run `4.` again with `good_clean_frame_number` specified 
    - Note - these two things are independent of each other, but probably would work well if you use the same frame number for both