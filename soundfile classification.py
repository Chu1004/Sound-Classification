import os
import numpy as np
import soundfile as sf
from scipy.signal import spectrogram
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.metrics import accuracy_score


# 設定參數
SAMPLE_RATE = 22050  # 採樣率
DURATION = 2         # 每段音頻的秒數
CLASSES = ["human_voice", "instrument", "noise"]  # 類別標籤

# 提取音頻特徵 (頻譜相關)
def extract_features(signal, sample_rate=SAMPLE_RATE, n_fft=1024, hop_length=512):
    freqs, times, Sxx = spectrogram(signal, fs=sample_rate, nperseg=n_fft, noverlap=hop_length)
    probability_distribution = Sxx / np.sum(Sxx, axis=0, keepdims=True)
    spectral_centroid = np.sum(freqs[:, None] * Sxx, axis=0) / np.sum(Sxx, axis=0)
    spectral_features = np.hstack([
        np.mean(Sxx, axis=1),  # 頻譜平均值
        np.std(Sxx, axis=1),    # 頻譜標準差
        #np.max(Sxx, axis=1)
    ])
    
    return spectral_features

# 加載數據並提取特徵
def load_data(data_dir):
    X, y = [], []
    for label, class_name in enumerate(CLASSES):
        class_dir = os.path.join(data_dir, class_name)
        if not os.path.exists(class_dir):
            print(f"Warning: Directory {class_dir} does not exist. Skipping.")
            continue
        for file_name in os.listdir(class_dir):
            file_path = os.path.join(class_dir, file_name)
            signal, _ = sf.read(file_path)  # 讀取音頻文件
            signal = signal[:SAMPLE_RATE * DURATION]  # 裁剪音頻
            if len(signal) < SAMPLE_RATE * DURATION:  # 若不足指定長度，補零
                signal = np.pad(signal, (0, SAMPLE_RATE * DURATION - len(signal)))
            features = extract_features(signal)  # 提取特徵
            X.append(features)
            #print(features)
            y.append(label)
    return np.array(X), np.array(y)

# 構建分類器並訓練
def train_model(X_train, y_train):
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    return clf

# 主程式
def main():
    # 1. 加載數據
    data_dir = "C:\\Users\\Administrator\\Desktop\\data\\"  # 設定音頻數據路徑
    X, y = load_data(data_dir)
    print(X)
    if X.shape[0] == 0:
        print("No data found. Please check your data directory.")
        return
    
    # 2. 分割訓練集和測試集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42)
    
    # 3. 訓練模型
    model = train_model(X_train, y_train)
    
    # 4. 預測並評估
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(classification_report(y_test, y_pred, target_names=CLASSES))
    print(f"Test Accuracy: {accuracy * 100:.2f}%")

if __name__ == "__main__":
    main()
