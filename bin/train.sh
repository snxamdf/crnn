if [ "$1" = "stop" ]; then
    echo "停止训练"
    kill -9 `ps aux|grep crnn| grep -v grep|awk '{print $2}'`
    exit
fi

if [ "$1" = "console" ]; then

    # 第一句表明使用第0个GPU，CRNN用第0个GPU，CTPN用第1个GPU，恩，我这么分配的
    CUDA_VISIBLE_DEVICES=0 \
    python \
        -m tools.train \
        --train_dir=data/train \
        --label_file=data/train.txt \
        --name=crnn \
        --validate_steps=10000 \
        --tboard_dir=tboard \
        --debug=True

else

    # 第一句表明使用第0个GPU，CRNN用第0个GPU，CTPN用第1个GPU，恩，我这么分配的
    CUDA_VISIBLE_DEVICES=0 \
    python \
        -m tools.train \
        --train_dir=data/train \
        --label_file=train.txt \
        --name=crnn \
        --validate_steps=1000 \
        --tboard_dir=tboard \
        --debug=True \
        >> ./logs/crnn.log 2>&1
fi
#    --weights_path=model/shadownet/shadownet_2019-03-11-15-13-38.ckpt-8 \
