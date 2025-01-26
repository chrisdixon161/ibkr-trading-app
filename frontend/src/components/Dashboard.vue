<template>
	<div class="dashboard">
		<h1 class="text-2xl font-bold mb-4">IBKR Dashboard</h1>

		<p v-if="error" class="text-red-500">Error: {{ error }}</p>

		<!-- retrieve IBKR account data -->
		<div class="card mb-6">
			<h2 class="text-xl font-semibold mb-2">Account Summary</h2>
			<p><strong>Current Account: </strong>{{ currentAccount }}</p>
			<div v-if="accountData" class="mt-4">
				<div v-for="(item, index) in accountData" :key="index">
					<p
						v-if="
							item.tag === 'FullAvailableFunds' &&
							item.account === currentAccount
						"
					>
						<strong>Balance: </strong>{{ item.value }} {{ item.currency }}
					</p>
				</div>
			</div>
		</div>

		<!-- place an options trade -->
		<div class="card">
			<h2 class="text-xl font-semibold mb-2">Place Options Trade</h2>
			<form @submit.prevent="placeTrade">
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="block font-medium">Symbol</label>
						<input
							v-model="tradeData.symbol"
							type="text"
							class="input"
							placeholder="e.g., AAPL"
							required
						/>
					</div>
					<div>
						<label class="block font-medium">Expiry Date</label>
						<input
							v-model="tradeData.expiry"
							type="date"
							class="input"
							required
						/>
					</div>
					<div>
						<label class="block font-medium">Strike Price</label>
						<input
							v-model.number="tradeData.strike"
							type="number"
							step="0.01"
							class="input"
							placeholder="e.g., 150"
							required
						/>
					</div>
					<div>
						<label class="block font-medium">Right</label>
						<select v-model="tradeData.right" class="input" required>
							<option value="C">Call</option>
							<option value="P">Put</option>
						</select>
					</div>
					<div>
						<label class="block font-medium">Quantity</label>
						<input
							v-model.number="tradeData.quantity"
							type="number"
							class="input"
							placeholder="e.g., 1"
							required
						/>
					</div>
					<div>
						<label class="block font-medium">Action</label>
						<select v-model="tradeData.action" class="input" required>
							<option value="BUY">Buy</option>
							<option value="SELL">Sell</option>
						</select>
					</div>
					<div>
						<label class="block font-medium">Order Type</label>
						<select v-model="tradeData.order_type" class="input" required>
							<option value="MKT">Market</option>
							<option value="LMT">Limit</option>
						</select>
					</div>
					<div v-if="tradeData.order_type === 'LMT'">
						<label class="block font-medium">Limit Price</label>
						<input
							v-model.number="tradeData.limit_price"
							type="number"
							step="0.01"
							class="input"
							placeholder="e.g., 145"
						/>
					</div>
				</div>
				<button
					type="submit"
					class="btn bg-green-500 text-white hover:bg-green-600 mt-4"
				>
					Place Trade
				</button>
			</form>
			<div v-if="tradeResponse" class="mt-4">
				<h3 class="font-semibold">Trade Response:</h3>
				<pre>{{ tradeResponse }}</pre>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, watch } from "vue";
import axios from "axios";

const accountData = ref(null);
const currentAccount = ref("");
const selectedFunds = ref("");
const tradeData = ref({
	symbol: "SPY",
	expiry: "",
	strike: null,
	right: "C", // Default to Call
	quantity: 1,
	action: "BUY", // Default to Buy
	order_type: "MKT", // Default to Market Order
	limit_price: null, // Only used for Limit Orders
});
const tradeResponse = ref(null);
const error = ref(null);

// Fetch account data and the current account automatically on component load
const fetchAccountData = async () => {
	try {
		// Fetch all account data
		const accountResponse = await axios.get(
			"http://127.0.0.1:8000/api/ibkr/account-data"
		);
		accountData.value = accountResponse.data.account_data;

		// Fetch the current account
		const currentAccountResponse = await axios.get(
			"http://127.0.0.1:8000/api/ibkr/current-account"
		);
		currentAccount.value = currentAccountResponse.data.current_account;

		// Find funds for the current account
		const account = accountData.value.find(
			(item) => item.account === currentAccount.value
		);
		selectedFunds.value = account?.value || "Not Available";

		error.value = null;
	} catch (err) {
		console.error("Error fetching account data:", err);
		error.value =
			err.response?.data?.detail || "Failed to retrieve account data.";
	}
};

// Automatically fetch data when the component is mounted
onMounted(fetchAccountData);

// Watch for changes in the `currentAccount` and update funds dynamically
watch(currentAccount, () => {
	const account = accountData.value?.find(
		(item) => item.account === currentAccount.value
	);
	selectedFunds.value = account?.value || "Not Available";
});

// Place trade function
const placeTrade = async () => {
	try {
		const response = await axios.post(
			"http://127.0.0.1:8000/api/ibkr/place-option-trade",
			tradeData.value
		);
		tradeResponse.value = response.data;
		error.value = null;
	} catch (err) {
		console.error("Error placing trade:", err);
		error.value = err.response?.data?.detail || "Failed to place trade.";
	}
};
</script>

<style scoped>
.card {
	padding: 1rem;
	margin-bottom: 1rem;
	border: 1px solid #e5e7eb;
	border-radius: 0.5rem;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
.input {
	width: 100%;
	padding: 0.5rem;
	margin-top: 0.25rem;
	border: 1px solid #e5e7eb;
	border-radius: 0.25rem;
}
.btn {
	padding: 0.5rem 1rem;
	font-weight: 500;
	border-radius: 0.25rem;
	cursor: pointer;
}
</style>
