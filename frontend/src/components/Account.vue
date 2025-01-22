<script setup>
import { supabase } from "../supabase";
import { onMounted, ref, toRefs } from "vue";

const props = defineProps(["session"]);
const { session } = toRefs(props);

const loading = ref(true);
const username = ref("");
const website = ref("");
const avatar_url = ref("");

onMounted(() => {
	getProfile();
});

async function getProfile() {
	try {
		loading.value = true;
		const { user } = session.value;

		const { data, error, status } = await supabase
			.from("profiles")
			.select(`username, website, avatar_url`)
			.eq("id", user.id)
			.single();

		if (error && status !== 406) throw error;

		if (data) {
			username.value = data.username;
			website.value = data.website;
			avatar_url.value = data.avatar_url;
		}
	} catch (error) {
		alert(error.message);
	} finally {
		loading.value = false;
	}
}

async function updateProfile() {
	try {
		loading.value = true;
		const { user } = session.value;

		const updates = {
			id: user.id,
			username: username.value,
			website: website.value,
			avatar_url: avatar_url.value,
			updated_at: new Date(),
		};

		const { error } = await supabase.from("profiles").upsert(updates);

		if (error) throw error;
	} catch (error) {
		alert(error.message);
	} finally {
		loading.value = false;
	}
}

async function signOut() {
	try {
		loading.value = true;
		const { error } = await supabase.auth.signOut();
		if (error) throw error;
	} catch (error) {
		alert(error.message);
	} finally {
		loading.value = false;
	}
}
</script>

<template>
	<form class="form-widget" @submit.prevent="updateProfile">
		<ul>
			<li v-for="(key, val) in session.user" :key="key.id">
				<strong>{{ val }}:</strong> {{ key }}
			</li>
		</ul>
		<div>
			<button class="button block" @click="signOut" :disabled="loading">
				Sign Out
			</button>
		</div>
	</form>
</template>
