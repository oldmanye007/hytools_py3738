
# python /home/ye6/hys_test/test_ftps/data/exec_ht.py /home/ye6/hys_test/test_ftps/data/f130410t01p00r09rdn_refl_img_corr  /home/ye6/hys_test/test_ftps/data/f130410t01p00r09rdn_e_obs_ort  /home/ye6/hys_test/test_ftps/data/

import sys

#sys.path.append('/home/ye6/hys_test/gdrive_test/temp/for_netcdf_chtc_grouptopo')

import hytools as ht
from hytools.misc import set_glint
from hytools.topo.topo import calc_topo_coeffs_single
from hytools.brdf.brdf import calc_brdf_coeffs_pre,calc_flex_single_post  #calc_brdf_coeffs
import matplotlib.pyplot as plt
import numpy as np

import correct_setting

envi_image= sys.argv[1] #f130410t01p00r09rdn_refl_img_corr
obs_ort_image = sys.argv[2]  #f130410t01p00r09rdn_e_obs_ort

cmap = plt.cm.gray.copy()
cmap.set_bad(color='none')

out_dir = sys.argv[3]  #"./data/"

anc_data = {'path_length': [obs_ort_image, 0],
 'sensor_az': [obs_ort_image, 1],
 'sensor_zn': [obs_ort_image, 2],
 'solar_az': [obs_ort_image, 3],
 'solar_zn': [obs_ort_image, 4],
 'phase': [obs_ort_image, 5],
 'slope': [obs_ort_image, 6],
 'aspect': [obs_ort_image, 7],
 'cosine_i': [obs_ort_image, 8],
 'utc_time': [obs_ort_image, 9]}


def show_rgb(hy_obj,ax,r=660,g=550,b=440, correct= []):

    rgb=  np.stack([hy_obj.get_wave(r,corrections= correct),
                    hy_obj.get_wave(g,corrections= correct),
                    hy_obj.get_wave(b,corrections= correct)])
    rgb = np.moveaxis(rgb,0,-1).astype(float)
    rgb[rgb ==hy_obj.no_data] = np.nan

    bottom = np.nanpercentile(rgb,5,axis = (0,1))
    top = np.nanpercentile(rgb,95,axis = (0,1))
    rgb = np.clip(rgb,bottom,top)

    rgb = (rgb-np.nanmin(rgb,axis=(0,1)))/(np.nanmax(rgb,axis= (0,1))-np.nanmin(rgb,axis= (0,1)))

    height = int(hy_obj.lines/hy_obj.columns)

    #fig  = plt.figure(figsize = (7,7) )
    ax.imshow(rgb)
    #plt.show()
    #plt.close()

def get_wave(wave,wavelengths):
    """Return the band image corresponding to the input wavelength.
    If not an exact match the closest wavelength will be returned.
    Args:
        wave (float): Wavelength in image units.
        wavelengths (list): Wavelength list

    Returns:
        band index 0-based.

    """

    if (wave  > wavelengths.max()) | (wave  < wavelengths.min()):
        print("Input wavelength outside wavelength range!")
        band_ind = None
    else:
        band_ind = np.argmin(np.abs(wavelengths - wave))
    return band_ind

envi_obj = ht.HyTools()
envi_obj.read_file(envi_image,'envi',anc_path=anc_data)

brdf_internal_dict = {}
brdf_internal_dict['bad_bands'] = correct_setting.BAD_BAND_RANGE #[[300,405],[1337,1430],[1800,1960],[2450,2600]]

envi_obj.create_bad_bands(brdf_internal_dict['bad_bands'])
#print(envi_obj.bad_bands)
print(envi_obj.wavelengths.shape)
#exit()
print(envi_obj.map_info)

#band = envi_obj.get_band(10)

#band = np.copy(band).astype(np.float32)
#band[~envi_obj.mask['no_data']] = np.nan

fig, ax = plt.subplots(2,3,figsize=(9,10))
#plt.matshow(band)
#ax[0,0].matshow(band)

#ax[1,0].matshow(envi_obj.mask['no_data'])

show_rgb(envi_obj,ax[0,0],r=660,g=550,b=440, correct= [])
ax[0,0].set_title("L2 Reflectance")

#set_glint(envi_obj,glint_setting)
set_glint(envi_obj,correct_setting.glint_setting_gao)

#print(envi_obj.corrections)
show_rgb(envi_obj,ax[0,1],r=660,g=550,b=440, correct= ['glint'])
ax[0,1].set_title("Sunglint corrected")


#band_corr_ratio = envi_obj.get_wave(550,corrections=['glint']) / envi_obj.get_wave(550,corrections=[])
#band_corr_diff = envi_obj.get_wave(550,corrections=['glint']) - envi_obj.get_wave(550,corrections=[])
#ax[1,2].imshow(band_corr_diff)

calc_topo_coeffs_single(envi_obj,correct_setting.topo_dict)

brdf_internal_dict['brdf'] = correct_setting.brdf_dict
combine_data_dict = calc_brdf_coeffs_pre(envi_obj,brdf_internal_dict)
combine_data_dict['bad_bands'] = envi_obj.bad_bands
#print(combine_data_dict["reflectance_samples"].shape)

sample_nir=combine_data_dict["reflectance_samples"][:,get_wave(850,np.array(combine_data_dict["used_band"]))]
sample_red=combine_data_dict["reflectance_samples"][:,get_wave(660,np.array(combine_data_dict["used_band"]))]
sample_ndi = (sample_nir-sample_red)/(sample_nir+sample_red)
combine_data_dict["ndi_samples"] = sample_ndi

combine_data_dict["kernels_samples"] = combine_data_dict.pop("kernel_samples")
#print(combine_data_dict.keys())
calc_flex_single_post(combine_data_dict,correct_setting.brdf_dict,0)

show_rgb(envi_obj,ax[1,0],r=660,g=550,b=440, correct= ['topo','brdf'])
ax[1,0].set_title("TOPO-BRDF corrected")


band_corr_ratio = envi_obj.get_wave(550,corrections=['topo','brdf']) / envi_obj.get_wave(550,corrections=[])
#band_corr_diff = envi_obj.get_wave(550,corrections=['glint']) - envi_obj.get_wave(550,corrections=[])
ax[1,1].imshow(band_corr_ratio)
ax[1,1].set_title("TOPO-BRDF correcting ratio")

#print(np.count_nonzero(np.isnan(band_corr_ratio)))

#ax[1,1].imshow(envi_obj.mask['apply_topo'])
region2 = envi_obj.mask['calc_brdf'] #.copy()
#region2[np.isnan(band_corr_ratio)] = np.nan
ax[1,2].imshow(region2,cmap=cmap)
ax[1,2].set_title("TOPO-BRDF correct region")

region1 = envi_obj.mask['apply_glint'] #.copy()
#region1[np.isnan(band_corr_ratio)] = np.nan
ax[0,2].imshow(region1,cmap=cmap)
ax[0,2].set_title("Sunglint correct region")


#ax[1,2].imshow(envi_obj.mask['apply_brdf'])

fig.savefig(f"{out_dir}/test_plot.png")
