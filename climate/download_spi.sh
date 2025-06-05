for year in {2007..2025}; do
    for TS in 1 3 6 12; do
        aws s3 cp s3://edogdo/store/spi/chirps2/spi/spi${TS}/${year}/ \
            /home/sadc/share/project/calabria/data/raw/spi/${TS}/${year}/ \
            --recursive \
            --exclude "*" \
            --include "*CHIRPS2-SPI${TS}_*_tile*.tif" \
            
    done
done


# for TS in 1 3 6 12; do
#     aws s3 cp s3://edogdo/store/spi/chirps2/spi/spi${TS}/2006/ \
#         /home/sadc/share/project/calabria/data/raw/spi/${TS}/2006/ \
#         --recursive \
#         --exclude "*" \
#         --include "*CHIRPS2-SPI${TS}_*_tile*.tif" \
        
# done

